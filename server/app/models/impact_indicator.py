import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class ImpactIndicator(UUIDPKMixin, TimestampMixin, Base):
    """A single measurable indicator declared for a Project before
    implementation (baseline) and evaluated after (endline). Verification is
    a separate, explicit step — a project reaching COMPLETED status does not
    by itself verify any claimed impact."""

    __tablename__ = "impact_indicators"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)

    baseline_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    baseline_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    target_value: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Claimed (unverified) endline figures — set by Faculty.
    actual_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    endline_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    endline_evidence: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Verified impact — a distinct step, set only by an authorized reviewer.
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=True, index=True
    )
