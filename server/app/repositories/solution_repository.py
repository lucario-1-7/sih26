from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.solution import Solution
from app.repositories.base import BaseRepository


class SolutionRepository(BaseRepository):
    async def get(self, solution_id: uuid.UUID) -> Solution | None:
        solution = await self.db.get(Solution, solution_id)
        if solution is None or solution.deleted_at is not None:
            return None
        return solution

    async def list(self, *, project_id: uuid.UUID | None, limit: int = 20, offset: int = 0) -> list[Solution]:
        stmt = select(Solution).where(Solution.deleted_at.is_(None))
        if project_id is not None:
            stmt = stmt.where(Solution.project_id == project_id)
        stmt = stmt.order_by(Solution.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, *, project_id: uuid.UUID, title: str, description: str | None) -> Solution:
        solution = Solution(project_id=project_id, title=title, description=description)
        self.db.add(solution)
        await self.db.flush()
        return solution
