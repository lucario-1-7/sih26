import uuid

from sqlalchemy import select

from app.core.pagination import paginate
from app.models.administrative_area import AdministrativeArea
from app.models.enums import AdministrativeLevel
from app.repositories.base import BaseRepository


class AdministrativeAreaRepository(BaseRepository):
    async def get(self, area_id: uuid.UUID) -> AdministrativeArea | None:
        return await self.db.get(AdministrativeArea, area_id)

    async def list(
        self,
        *,
        level: AdministrativeLevel | None = None,
        parent_id: uuid.UUID | None = None,
        search: str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> tuple[list[AdministrativeArea], str | None]:
        stmt = select(AdministrativeArea)
        if level is not None:
            stmt = stmt.where(AdministrativeArea.level == level)
        if parent_id is not None:
            stmt = stmt.where(AdministrativeArea.parent_id == parent_id)
        if search:
            stmt = stmt.where(AdministrativeArea.name.ilike(f"%{search}%"))
        return await paginate(self.db, stmt, model=AdministrativeArea, limit=limit, cursor=cursor)
