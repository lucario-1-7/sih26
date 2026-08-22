import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin, pg_enum
from app.models.enums import AdministrativeLevel


class AdministrativeArea(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "administrative_areas"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    level: Mapped[AdministrativeLevel] = mapped_column(
        pg_enum(AdministrativeLevel, "administrative_level"), nullable=False, index=True
    )
    lgd_code: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("administrative_areas.id", ondelete="RESTRICT"), nullable=True, index=True
    )

    parent: Mapped["AdministrativeArea | None"] = relationship(
        remote_side="AdministrativeArea.id", back_populates="children"
    )
    children: Mapped[list["AdministrativeArea"]] = relationship(back_populates="parent")
