from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.cluster import Cluster
from app.models.enums import ClusterStatus
from app.repositories.base import BaseRepository


class ClusterRepository(BaseRepository):
    async def get(self, cluster_id: uuid.UUID) -> Cluster | None:
        cluster = await self.db.get(Cluster, cluster_id)
        if cluster is None or cluster.deleted_at is not None:
            return None
        return cluster

    async def list(
        self, *, status: ClusterStatus | None = None, limit: int = 20, offset: int = 0
    ) -> list[Cluster]:
        stmt = select(Cluster).where(Cluster.deleted_at.is_(None))
        if status is not None:
            stmt = stmt.where(Cluster.status == status)
        stmt = stmt.order_by(Cluster.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, *, title: str, description: str | None, theme_id: uuid.UUID | None) -> Cluster:
        cluster = Cluster(title=title, description=description, theme_id=theme_id)
        self.db.add(cluster)
        await self.db.flush()
        return cluster
