from __future__ import annotations

import uuid

from sqlalchemy import select

from app.core.pagination import paginate
from app.models.impact_indicator import ImpactIndicator
from app.repositories.base import BaseRepository


class ImpactIndicatorRepository(BaseRepository):
    async def get(self, indicator_id: uuid.UUID) -> ImpactIndicator | None:
        return await self.db.get(ImpactIndicator, indicator_id)

    async def list_for_project(
        self, project_id: uuid.UUID, *, limit: int = 20, cursor: str | None = None
    ) -> tuple[list[ImpactIndicator], str | None]:
        stmt = select(ImpactIndicator).where(ImpactIndicator.project_id == project_id)
        return await paginate(self.db, stmt, model=ImpactIndicator, limit=limit, cursor=cursor)

    async def create(
        self,
        *,
        project_id: uuid.UUID,
        name: str,
        unit: str,
        baseline_value: float | None,
        baseline_date,
        target_value: float | None,
    ) -> ImpactIndicator:
        indicator = ImpactIndicator(
            project_id=project_id,
            name=name,
            unit=unit,
            baseline_value=baseline_value,
            baseline_date=baseline_date,
            target_value=target_value,
        )
        self.db.add(indicator)
        await self.db.flush()
        return indicator
