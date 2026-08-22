import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin, pg_enum
from app.models.enums import ConsortiumStatus


class Consortium(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "consortiums"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    status: Mapped[ConsortiumStatus] = mapped_column(
        pg_enum(ConsortiumStatus, "consortium_status"),
        nullable=False,
        default=ConsortiumStatus.PROPOSED,
    )


class ConsortiumMember(UUIDPKMixin, Base):
    __tablename__ = "consortium_members"
    __table_args__ = (
        UniqueConstraint("consortium_id", "organization_id", name="uq_consortium_member_pair"),
    )

    consortium_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("consortiums.id", ondelete="CASCADE"), nullable=False, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
