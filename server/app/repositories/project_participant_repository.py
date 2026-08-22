from __future__ import annotations

import uuid

from sqlalchemy import select

from app.core.pagination import paginate
from app.models.project_participant import ProjectParticipant
from app.repositories.base import BaseRepository


class ProjectParticipantRepository(BaseRepository):
    async def get(self, participant_id: uuid.UUID) -> ProjectParticipant | None:
        return await self.db.get(ProjectParticipant, participant_id)

    async def list_for_project(
        self, project_id: uuid.UUID, *, limit: int = 20, cursor: str | None = None
    ) -> tuple[list[ProjectParticipant], str | None]:
        stmt = select(ProjectParticipant).where(ProjectParticipant.project_id == project_id)
        return await paginate(self.db, stmt, model=ProjectParticipant, limit=limit, cursor=cursor)

    async def create(
        self,
        *,
        project_id: uuid.UUID,
        name: str,
        department: str | None,
        academic_year: str | None,
        registration_id: str | None,
        participation_role: str,
    ) -> ProjectParticipant:
        participant = ProjectParticipant(
            project_id=project_id,
            name=name,
            department=department,
            academic_year=academic_year,
            registration_id=registration_id,
            participation_role=participation_role,
        )
        self.db.add(participant)
        await self.db.flush()
        return participant
