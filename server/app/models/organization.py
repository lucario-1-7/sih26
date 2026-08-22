from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPKMixin, pg_enum
from app.models.enums import OrganizationType


class Organization(UUIDPKMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[OrganizationType] = mapped_column(
        pg_enum(OrganizationType, "organization_type"), nullable=False, index=True
    )
    domain_tags: Mapped[list[str]] = mapped_column(ARRAY(String(100)), nullable=False, default=list)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)
