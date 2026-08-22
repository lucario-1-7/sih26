import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin, pg_enum
from app.models.enums import CollaborationStatus, CollaborationType, CommitmentStatus


class Collaboration(UUIDPKMixin, TimestampMixin, Base):
    """A bilateral partnership between one Organization (industry, typically)
    and one Project. Distinct from Consortium, which represents the
    multi-organization ML-suggested team formed for a project up front —
    a Collaboration is an individual org's own engagement lifecycle with a
    project, initiated by that org expressing interest."""

    __tablename__ = "collaborations"
    __table_args__ = (UniqueConstraint("organization_id", "project_id", name="uq_collaboration_org_project"),)

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[CollaborationType] = mapped_column(
        pg_enum(CollaborationType, "collaboration_type"), nullable=False
    )
    status: Mapped[CollaborationStatus] = mapped_column(
        pg_enum(CollaborationStatus, "collaboration_status"),
        nullable=False,
        default=CollaborationStatus.INTERESTED,
    )
    proposal: Mapped[str | None] = mapped_column(Text, nullable=True)


class CollaborationCommitment(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "collaboration_commitments"

    collaboration_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("collaborations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[CollaborationType] = mapped_column(
        pg_enum(CollaborationType, "collaboration_type"), nullable=False
    )
    amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[CommitmentStatus] = mapped_column(
        pg_enum(CommitmentStatus, "commitment_status"), nullable=False, default=CommitmentStatus.PROPOSED
    )
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
