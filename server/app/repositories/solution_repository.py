from __future__ import annotations

import uuid

from sqlalchemy import select

from app.core.pagination import paginate
from app.models.solution import Solution
from app.repositories.base import BaseRepository


class SolutionRepository(BaseRepository):
    async def get(self, solution_id: uuid.UUID) -> Solution | None:
        solution = await self.db.get(Solution, solution_id)
        if solution is None or solution.deleted_at is not None:
            return None
        return solution

    async def list(
        self, *, project_id: uuid.UUID | None, limit: int = 20, cursor: str | None = None
    ) -> tuple[list[Solution], str | None]:
        stmt = select(Solution).where(Solution.deleted_at.is_(None))
        if project_id is not None:
            stmt = stmt.where(Solution.project_id == project_id)
        return await paginate(self.db, stmt, model=Solution, limit=limit, cursor=cursor)

    async def create(
        self,
        *,
        project_id: uuid.UUID,
        title: str,
        description: str | None,
        outcome: str | None,
        embedding: list[float] | None,
    ) -> Solution:
        solution = Solution(
            project_id=project_id, title=title, description=description, outcome=outcome, embedding=embedding
        )
        self.db.add(solution)
        await self.db.flush()
        return solution
