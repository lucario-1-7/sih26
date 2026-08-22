import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    TokenType,
    create_token,
    decode_token,
    generate_otp,
    hash_otp,
    verify_otp_hash,
)
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import OtpRepository, UserRepository
from app.schemas.auth import TokenPair
from app.services.otp_dev_store import store_dev_otp
from app.services.otp_sender import get_otp_sender
from app.services.token_store import is_refresh_jti_valid, revoke_refresh_jti, store_refresh_jti


async def request_otp(db: AsyncSession, *, phone: str, ip_address: str | None) -> None:
    settings = get_settings()
    user_repo = UserRepository(db)
    otp_repo = OtpRepository(db)
    audit_repo = AuditRepository(db)

    user = await user_repo.get_or_create_by_phone(phone)

    code = generate_otp(settings.OTP_LENGTH)
    code_hash = hash_otp(code, phone)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    await otp_repo.create(phone=phone, code_hash=code_hash, expires_at=expires_at)

    await audit_repo.log(
        user_id=user.id,
        action="auth.otp_requested",
        entity_type="user",
        entity_id=user.id,
        ip_address=ip_address,
    )
    await db.commit()

    # Development convenience only — no-ops outside ENVIRONMENT=development
    # (see otp_dev_store), never logged, never returned by the production API.
    store_dev_otp(phone, code)

    await get_otp_sender().send(phone, code)


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

    if not verify_otp_hash(code, phone, otp.code_hash):
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
