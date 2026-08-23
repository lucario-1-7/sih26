from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.pagination import paginate
from app.models.enums import Domain, Role
from app.models.user import OtpCode, User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    async def get(self, user_id: uuid.UUID) -> User | None:
        return await self.db.get(User, user_id)

    async def create(
        self,
        *,
        phone: str,
        name: str,
        role: Role,
        domain: Domain,
        organization_id: uuid.UUID | None,
        administrative_area_id: uuid.UUID | None,
    ) -> User:
        user = User(
            phone=phone,
            name=name,
            role=role,
            domain=domain,
            organization_id=organization_id,
            administrative_area_id=administrative_area_id,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def get_by_phone(self, phone: str) -> User | None:
        result = await self.db.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    async def get_or_create_by_phone(self, phone: str, name: str = "") -> User:
        user = await self.get_by_phone(phone)
        if user is not None:
            return user
        user = User(phone=phone, name=name or phone, role=Role.CITIZEN)
        self.db.add(user)
        await self.db.flush()
        return user

    async def get_or_create_demo_user(
        self,
        *,
        phone: str,
        name: str,
        role: Role,
        domain: Domain,
        organization_id: uuid.UUID | None,
    ) -> User:
        """PRESENTATION-ONLY (see auth_service.demo_login). Idempotent by
        phone, exactly like get_or_create_by_phone — a real, persisted row
        with a real role/domain/organization, not a fabricated in-memory
        object, so every downstream RBAC check and query behaves exactly as
        it would for a genuinely logged-in user."""
        user = await self.get_by_phone(phone)
        if user is not None:
            return user
        user = User(
            phone=phone,
            name=name,
            role=role,
            domain=domain,
            organization_id=organization_id,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def list(
        self, *, role: Role | None = None, limit: int = 20, cursor: str | None = None
    ) -> tuple[list[User], str | None]:
        stmt = select(User).where(User.deleted_at.is_(None))
        if role is not None:
            stmt = stmt.where(User.role == role)
        return await paginate(self.db, stmt, model=User, limit=limit, cursor=cursor)


class OtpRepository(BaseRepository):
    async def create(
        self,
        *,
        phone: str,
        expires_at: datetime,
        code_hash: str | None = None,
        provider_ref: str | None = None,
    ) -> OtpCode:
        otp = OtpCode(phone=phone, code_hash=code_hash, provider_ref=provider_ref, expires_at=expires_at)
        self.db.add(otp)
        await self.db.flush()
        return otp

    async def get_latest_active(self, phone: str) -> OtpCode | None:
        stmt = (
            select(OtpCode)
            .where(OtpCode.phone == phone, OtpCode.used_at.is_(None))
            .order_by(OtpCode.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_used(self, otp: OtpCode) -> None:
        otp.used_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def increment_attempts(self, otp: OtpCode) -> None:
        otp.attempt_count += 1
        await self.db.flush()
