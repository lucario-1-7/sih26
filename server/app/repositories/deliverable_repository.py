from __future__ import annotations

import uuid

from sqlalchemy import select

from app.core.pagination import paginate
from app.models.deliverable import Deliverable
from app.repositories.base import BaseRepository


class DeliverableRepository(BaseRepository):
    async def get(self, deliverable_id: uuid.UUID) -> Deliverable | None:
        return await self.db.get(Deliverable, deliverable_id)

    async def list_for_project(
        self, project_id: uuid.UUID, *, limit: int = 20, cursor: str | None = None
    ) -> tuple[list[Deliverable], str | None]:
        stmt = select(Deliverable).where(Deliverable.project_id == project_id)
        return await paginate(self.db, stmt, model=Deliverable, limit=limit, cursor=cursor)

    async def create(
        self, *, project_id: uuid.UUID, title: str, description: str | None, due_date
    ) -> Deliverable:
        deliverable = Deliverable(project_id=project_id, title=title, description=description, due_date=due_date)
        self.db.add(deliverable)
        await self.db.flush()
        return deliverable
