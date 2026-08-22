from __future__ import annotations

import uuid

from sqlalchemy import select

from app.core.pagination import paginate
from app.models.milestone import Milestone
from app.repositories.base import BaseRepository


class MilestoneRepository(BaseRepository):
    async def get(self, milestone_id: uuid.UUID) -> Milestone | None:
        return await self.db.get(Milestone, milestone_id)

    async def list_for_project(
        self, project_id: uuid.UUID, *, limit: int = 20, cursor: str | None = None
    ) -> tuple[list[Milestone], str | None]:
        stmt = select(Milestone).where(Milestone.project_id == project_id)
        return await paginate(self.db, stmt, model=Milestone, limit=limit, cursor=cursor)

    async def create(
        self,
        *,
        project_id: uuid.UUID,
        title: str,
        description: str | None,
        due_date,
        order: int,
    ) -> Milestone:
        milestone = Milestone(
            project_id=project_id, title=title, description=description, due_date=due_date, order=order
        )
        self.db.add(milestone)
        await self.db.flush()
        return milestone
