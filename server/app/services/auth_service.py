import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.security import (
    TokenType,
    create_token,
    decode_token,
    generate_otp,
    hash_otp,
    verify_otp_hash,
)
from app.models.enums import Domain, OrganizationType, Role
from app.models.organization import Organization
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import OtpRepository, UserRepository
from app.schemas.auth import TokenPair
from app.services.otp_dev_store import store_dev_otp
from app.services.otp_sender import NativeOtpProvider, get_otp_sender
from app.services.token_store import is_refresh_jti_valid, revoke_refresh_jti, store_refresh_jti


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


async def request_otp(db: AsyncSession, *, phone: str, ip_address: str | None) -> None:
    settings = get_settings()
    user_repo = UserRepository(db)
    otp_repo = OtpRepository(db)
    audit_repo = AuditRepository(db)

    user = await user_repo.get_or_create_by_phone(phone)

    # Resend protection — independent of MSG91's own delivery-side
    # throttling, and independent of OTP expiry (an OTP can still be
    # unexpired and unused while this cooldown blocks a premature resend).
    existing = await otp_repo.get_latest_active(phone)
    if existing is not None:
        elapsed = (datetime.now(timezone.utc) - _aware(existing.created_at)).total_seconds()
        if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
            retry_after = int(settings.OTP_RESEND_COOLDOWN_SECONDS - elapsed)
            await audit_repo.log(
                user_id=user.id,
                action="auth.otp_resend_throttled",
                entity_type="user",
                entity_id=user.id,
                ip_address=ip_address,
                meta={"retry_after_seconds": retry_after},
            )
            await db.commit()
            raise AppError(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                code="OTP_RESEND_TOO_SOON",
                detail=f"Please wait {retry_after}s before requesting another code.",
            )

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    sender = get_otp_sender()

    if isinstance(sender, NativeOtpProvider):
        # The provider generates and owns the code — we never see it, so
        # there's nothing to hash and nothing to log even accidentally.
        # `send` must complete (and raise on failure) before we persist
        # anything, since the row is meaningless without a real provider_ref.
        provider_ref = await sender.send(phone)
        await otp_repo.create(phone=phone, provider_ref=provider_ref, expires_at=expires_at)
    else:
        code = generate_otp(settings.OTP_LENGTH)
        code_hash = hash_otp(code, phone)
        await otp_repo.create(phone=phone, code_hash=code_hash, expires_at=expires_at)

    await audit_repo.log(
        user_id=user.id,
        action="auth.otp_requested",
        entity_type="user",
        entity_id=user.id,
        ip_address=ip_address,
    )
    await db.commit()

    if not isinstance(sender, NativeOtpProvider):
        # Development convenience only — no-ops outside ENVIRONMENT=development
        # (see otp_dev_store), never logged, never returned by the production API.
        store_dev_otp(phone, code)
        await sender.send(phone, code)


async def verify_otp(db: AsyncSession, *, phone: str, code: str, ip_address: str | None) -> TokenPair:
    settings = get_settings()
    user_repo = UserRepository(db)
    otp_repo = OtpRepository(db)
    audit_repo = AuditRepository(db)

    user = await user_repo.get_by_phone(phone)
    otp = await otp_repo.get_latest_active(phone)

    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"detail": "Invalid or expired OTP", "code": "INVALID_OTP"},
    )

    if user is None or otp is None:
        await audit_repo.log(
            user_id=None, action="auth.login_failed", entity_type="user", ip_address=ip_address,
            meta={"phone": phone, "reason": "no_active_otp"},
        )
        await db.commit()
        raise invalid

    if otp.attempt_count >= settings.OTP_MAX_ATTEMPTS:
        await audit_repo.log(
            user_id=user.id, action="auth.login_failed", entity_type="user", entity_id=user.id,
            ip_address=ip_address, meta={"reason": "max_attempts_exceeded"},
        )
        await db.commit()
        raise invalid

    now = datetime.now(timezone.utc)
    expires_at = otp.expires_at if otp.expires_at.tzinfo else otp.expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now:
        await audit_repo.log(
            user_id=user.id, action="auth.login_failed", entity_type="user", entity_id=user.id,
            ip_address=ip_address, meta={"reason": "expired"},
        )
        await db.commit()
        raise invalid

    if otp.provider_ref is not None:
        sender = get_otp_sender()
        if not isinstance(sender, NativeOtpProvider):
            # Defensive only: the active provider changed (e.g. a config/env
            # flip) between this OTP being requested and now — there is no
            # correct way to verify a provider-native row without the
            # provider. Fail the verification, never crash.
            code_matches = False
        else:
            code_matches = await sender.verify(phone, code, otp.provider_ref)
    else:
        code_matches = verify_otp_hash(code, phone, otp.code_hash)

    if not code_matches:
        await otp_repo.increment_attempts(otp)
        await audit_repo.log(
            user_id=user.id, action="auth.login_failed", entity_type="user", entity_id=user.id,
            ip_address=ip_address, meta={"reason": "code_mismatch"},
        )
        await db.commit()
        raise invalid

    await otp_repo.mark_used(otp)
    await audit_repo.log(
        user_id=user.id, action="auth.login_succeeded", entity_type="user", entity_id=user.id,
        ip_address=ip_address,
    )
    await db.commit()

    return await _issue_tokens(user)


async def verify_msg91_widget_token(db: AsyncSession, *, access_token: str, ip_address: str | None) -> TokenPair:
    """Client-driven MSG91 OTP Widget flow (citizen web + Flutter): the
    client already completed the real OTP exchange directly with MSG91 and
    holds a widget-issued access-token. This confirms that token with MSG91
    server-side (the only call in this flow that uses the account-level
    MSG91_AUTH_KEY) and, from that point on, is identical to `verify_otp` —
    same `get_or_create_by_phone`, same `_issue_tokens`, same audit action
    family. There is no separate customer/session model for this path.

    Never trusts a phone number the client might have sent alongside the
    token — the verified phone comes only from MSG91's own response.
    """
    from app.services import otp_msg91

    user_repo = UserRepository(db)
    audit_repo = AuditRepository(db)

    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"detail": "Could not verify this sign-in — please try again.", "code": "INVALID_ACCESS_TOKEN"},
    )

    # A transport-level MSG91 failure (timeout/5xx/malformed) raises
    # OtpDeliveryError here, uncaught — mapped to a 503 by the global
    # handler, exactly like every other MSG91 call, never disguised as an
    # auth failure.
    phone = await otp_msg91.verify_widget_access_token(access_token)

    if phone is None:
        await audit_repo.log(
            user_id=None, action="auth.login_failed", entity_type="user", ip_address=ip_address,
            meta={"reason": "invalid_msg91_access_token"},
        )
        await db.commit()
        raise invalid

    user = await user_repo.get_or_create_by_phone(phone)
    await audit_repo.log(
        user_id=user.id, action="auth.login_succeeded", entity_type="user", entity_id=user.id,
        ip_address=ip_address, meta={"method": "msg91_widget"},
    )
    await db.commit()

    return await _issue_tokens(user)


# ---------------------------------------------------------------------------
# PRESENTATION-ONLY demo/bypass login. OFF by default (Settings.DEMO_MODE),
# force-disabled in production regardless of configuration (see
# app.core.config.Settings._demo_mode_never_in_production), and never
# activated as a fallback for a real provider failure — this is a wholly
# separate, explicit opt-in endpoint, not a degraded mode of real auth.
#
# Each persona resolves to a REAL, persisted User row (created idempotently
# by a fixed demo phone number, exactly like the real OTP flow's
# get_or_create_by_phone) with a real role/domain/organization and a real
# JWT from the same _issue_tokens() every other login path uses — so every
# RBAC check, every query, every ML/DB/Redis call downstream behaves
# identically to a genuine session. This bypasses only the OTP challenge
# itself, never authorization.
# ---------------------------------------------------------------------------

DEMO_PERSONAS: dict[str, tuple[Role, Domain, str, str | None]] = {
    # persona key -> (role, domain, demo phone, demo organization name)
    "citizen": (Role.CITIZEN, Domain.CITIZEN, "+910000000001", None),
    "government_validator": (Role.VALIDATOR, Domain.GOVERNMENT, "+910000000002", None),
    "government_field_assistant": (Role.FIELD_ASSISTANT, Domain.GOVERNMENT, "+910000000003", None),
    "university_coordinator": (Role.COORDINATOR, Domain.UNIVERSITY, "+910000000004", "Demo University"),
    "university_faculty": (Role.FACULTY, Domain.UNIVERSITY, "+910000000007", "Demo University"),
    "industry": (Role.INDUSTRY, Domain.INDUSTRY, "+910000000005", "Demo Industry Partner"),
    "superadmin": (Role.SUPERADMIN, Domain.SUPERADMIN, "+910000000006", None),
}

_ORG_TYPE_FOR_DOMAIN = {Domain.UNIVERSITY: OrganizationType.UNIVERSITY, Domain.INDUSTRY: OrganizationType.INDUSTRY}


async def demo_login(db: AsyncSession, *, persona: str, ip_address: str | None) -> TokenPair:
    settings = get_settings()
    if not settings.DEMO_MODE:
        # 404, not 403 — a disabled demo endpoint should look like it
        # doesn't exist, not hint at a feature to probe.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Not found", "code": "NOT_FOUND"})

    config = DEMO_PERSONAS.get(persona)
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"detail": f"Unknown demo persona '{persona}'.", "code": "UNKNOWN_DEMO_PERSONA"},
        )
    role, domain, phone, org_name = config

    organization_id = None
    if org_name is not None:
        result = await db.execute(select(Organization).where(Organization.name == org_name))
        org = result.scalar_one_or_none()
        if org is None:
            org = Organization(name=org_name, type=_ORG_TYPE_FOR_DOMAIN[domain], domain_tags=[])
            db.add(org)
            await db.flush()
        organization_id = org.id

    user_repo = UserRepository(db)
    audit_repo = AuditRepository(db)
    user = await user_repo.get_or_create_demo_user(
        phone=phone,
        name=f"Demo {persona.replace('_', ' ').title()}",
        role=role,
        domain=domain,
        organization_id=organization_id,
    )
    await audit_repo.log(
        user_id=user.id, action="auth.demo_login", entity_type="user", entity_id=user.id,
        ip_address=ip_address, meta={"persona": persona},
    )
    await db.commit()
    return await _issue_tokens(user)


async def refresh_tokens(db: AsyncSession, *, refresh_token: str) -> TokenPair:
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"detail": "Invalid or expired refresh token", "code": "UNAUTHORIZED"},
    )
    try:
        payload = decode_token(refresh_token)
    except jwt.InvalidTokenError:
        raise invalid

    if payload.get("type") != TokenType.REFRESH.value:
        raise invalid

    user_id = uuid.UUID(payload["sub"])
    jti = payload["jti"]

    if not await is_refresh_jti_valid(user_id, jti):
        raise invalid

    user = await UserRepository(db).get(user_id)
    if user is None or not user.is_active or user.deleted_at is not None:
        raise invalid

    await revoke_refresh_jti(user_id, jti)
    return await _issue_tokens(user)


async def logout(*, user_id: uuid.UUID, refresh_token: str) -> None:
    try:
        payload = decode_token(refresh_token)
    except jwt.InvalidTokenError:
        return
    if payload.get("type") == TokenType.REFRESH.value:
        await revoke_refresh_jti(user_id, payload["jti"])


async def _issue_tokens(user: User) -> TokenPair:
    settings = get_settings()
    access_token, _ = create_token(
        user_id=user.id,
        role=user.role.value,
        token_type=TokenType.ACCESS,
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    refresh_token, refresh_jti = create_token(
        user_id=user.id,
        role=user.role.value,
        token_type=TokenType.REFRESH,
        expires_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )
    await store_refresh_jti(user.id, refresh_jti)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)
