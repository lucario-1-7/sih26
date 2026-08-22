import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class ProjectParticipant(UUIDPKMixin, TimestampMixin, Base):
    """A student (or other non-platform participant) working on a Project.

    Students never get a login/JWT/role — Faculty/Coordinator maintain these
    records on their behalf through the project API.
    """

    __tablename__ = "project_participants"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[str | None] = mapped_column(String(200), nullable=True)
    academic_year: Mapped[str | None] = mapped_column(String(20), nullable=True)
    registration_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    participation_role: Mapped[str] = mapped_column(String(100), nullable=False, default="member")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
