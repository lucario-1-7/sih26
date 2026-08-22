import uuid

from app.models.administrative_area import AdministrativeArea
from app.repositories.base import BaseRepository


class AdministrativeAreaRepository(BaseRepository):
    async def get(self, area_id: uuid.UUID) -> AdministrativeArea | None:
        return await self.db.get(AdministrativeArea, area_id)
