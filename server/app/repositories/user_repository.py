from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.models.enums import Role
from app.models.user import OtpCode, User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    async def get(self, user_id: uuid.UUID) -> User | None:
        return await self.db.get(User, user_id)

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

    async def list(self, *, role: Role | None = None, limit: int = 20, offset: int = 0) -> list[User]:
        stmt = select(User).where(User.deleted_at.is_(None))
        if role is not None:
            stmt = stmt.where(User.role == role)
        stmt = stmt.order_by(User.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class OtpRepository(BaseRepository):
    async def create(self, *, phone: str, code_hash: str, expires_at: datetime) -> OtpCode:
        otp = OtpCode(phone=phone, code_hash=code_hash, expires_at=expires_at)
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
