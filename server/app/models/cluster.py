import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPKMixin, pg_enum
from app.models.enums import ClusterStatus


class Cluster(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "clusters"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    theme_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("themes.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    status: Mapped[ClusterStatus] = mapped_column(
        pg_enum(ClusterStatus, "cluster_status"), nullable=False, default=ClusterStatus.ACTIVE
    )
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)
