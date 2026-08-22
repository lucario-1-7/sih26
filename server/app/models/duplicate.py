import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Identity, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin, pg_enum
from app.models.enums import DuplicateDecisionType


class DuplicateCandidate(UUIDPKMixin, Base):
    __tablename__ = "duplicate_candidates"
    __table_args__ = (
        UniqueConstraint("challenge_id", "candidate_challenge_id", name="uq_duplicate_candidate_pair"),
    )

    challenge_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    candidate_challenge_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )


class DuplicateDecision(UUIDPKMixin, Base):
    """Append-only audit trail of human duplicate/not-duplicate decisions."""

    __tablename__ = "duplicate_decisions"

    challenge_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("challenges.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    candidate_challenge_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("challenges.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    decision: Mapped[DuplicateDecisionType] = mapped_column(
        pg_enum(DuplicateDecisionType, "duplicate_decision_type"), nullable=False
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    # Monotonic tiebreaker for "current effective decision" — created_at alone
    # can collide when two decisions on the same pair land in the same tick.
    sequence: Mapped[int] = mapped_column(BigInteger, Identity(always=True), nullable=False, unique=True)
