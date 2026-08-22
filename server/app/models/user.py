import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPKMixin, pg_enum
from app.models.enums import Domain, Role


class User(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "users"

    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[Role] = mapped_column(
        pg_enum(Role, "user_role"), nullable=False, default=Role.CITIZEN
    )
    domain: Mapped[Domain] = mapped_column(
        pg_enum(Domain, "user_domain"), nullable=False, default=Domain.CITIZEN
    )
    # University/industry staff belong to an Organization; government/citizen/
    # superadmin users leave this null.
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    administrative_area_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("administrative_areas.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class OtpCode(UUIDPKMixin, Base):
    __tablename__ = "otp_codes"

    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    code_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # `func.now()` (not the plain string "now()") — a raw string default gets
    # emitted as a quoted-literal DEFAULT that Postgres constant-folds once
    # at DDL time, freezing every row to the same timestamp. That exact bug
    # broke get_latest_active()'s ORDER BY created_at DESC (see migration
    # d4e5f6a7b8c9). func.now() (or sa.text("now()")) is the SQL function
    # call, correctly re-evaluated per row.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
