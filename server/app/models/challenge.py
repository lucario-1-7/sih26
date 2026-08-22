import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPKMixin, pg_enum
from app.models.enums import ChallengeStatus


class Challenge(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "challenges"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ChallengeStatus] = mapped_column(
        pg_enum(ChallengeStatus, "challenge_status"),
        nullable=False,
        default=ChallengeStatus.SUBMITTED,
        index=True,
    )
    submitted_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    administrative_area_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("administrative_areas.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    pin_code: Mapped[str | None] = mapped_column(String(6), nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)
    cluster_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("clusters.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    duplicate_of_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("challenges.id", ondelete="RESTRICT"), nullable=True, index=True
    )
