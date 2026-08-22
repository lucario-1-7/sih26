from __future__ import annotations

import uuid

from sqlalchemy import select

from app.core.pagination import paginate
from app.models.enums import OrganizationType
from app.models.organization import Organization
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository):
    async def get(self, org_id: uuid.UUID) -> Organization | None:
        org = await self.db.get(Organization, org_id)
        if org is None or org.deleted_at is not None:
            return None
        return org

    async def list(
        self, *, type: OrganizationType | None = None, limit: int = 20, cursor: str | None = None
    ) -> tuple[list[Organization], str | None]:
        stmt = select(Organization).where(Organization.deleted_at.is_(None))
        if type is not None:
            stmt = stmt.where(Organization.type == type)
        return await paginate(self.db, stmt, model=Organization, limit=limit, cursor=cursor)

    async def create(
        self,
        *,
        name: str,
        type: OrganizationType,
        domain_tags: list[str],
        description: str | None,
        embedding: list[float] | None,
    ) -> Organization:
        org = Organization(
            name=name, type=type, domain_tags=domain_tags, description=description, embedding=embedding
        )
        self.db.add(org)
        await self.db.flush()
        return org

    async def find_nearest_by_embedding(
        self, *, embedding: list[float], type: OrganizationType | None, limit: int
    ) -> list[Organization]:
        stmt = select(Organization).where(
            Organization.deleted_at.is_(None), Organization.embedding.is_not(None)
        )
        if type is not None:
            stmt = stmt.where(Organization.type == type)
        stmt = stmt.order_by(Organization.embedding.cosine_distance(embedding)).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
