import uuid

from sqlalchemy import select

from app.models.consortium import Consortium, ConsortiumMember
from app.repositories.base import BaseRepository


class ConsortiumRepository(BaseRepository):
    async def get(self, consortium_id: uuid.UUID) -> Consortium | None:
        return await self.db.get(Consortium, consortium_id)

    async def get_by_project(self, project_id: uuid.UUID) -> Consortium | None:
        result = await self.db.execute(select(Consortium).where(Consortium.project_id == project_id))
        return result.scalar_one_or_none()

    async def create(self, *, project_id: uuid.UUID) -> Consortium:
        consortium = Consortium(project_id=project_id)
        self.db.add(consortium)
        await self.db.flush()
        return consortium

    async def add_member(
        self,
        *,
        consortium_id: uuid.UUID,
        organization_id: uuid.UUID,
        role: str,
        match_score: float | None,
        rationale: str | None,
    ) -> ConsortiumMember:
        member = ConsortiumMember(
            consortium_id=consortium_id,
            organization_id=organization_id,
            role=role,
            match_score=match_score,
            rationale=rationale,
        )
        self.db.add(member)
        await self.db.flush()
        return member

    async def list_members(self, consortium_id: uuid.UUID) -> list[ConsortiumMember]:
        result = await self.db.execute(
            select(ConsortiumMember).where(ConsortiumMember.consortium_id == consortium_id)
        )
        return list(result.scalars().all())
