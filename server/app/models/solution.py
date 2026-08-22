import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPKMixin, pg_enum
from app.models.enums import SolutionStatus


class Solution(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "solutions"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[SolutionStatus] = mapped_column(
        pg_enum(SolutionStatus, "solution_status"), nullable=False, default=SolutionStatus.DRAFT
    )
    # Enables replication search (nearest-neighbor against open clusters).
    # Populated at creation — solutions are created infrequently, so this is
    # computed synchronously rather than via a background job.
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)
