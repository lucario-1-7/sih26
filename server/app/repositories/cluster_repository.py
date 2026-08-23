from __future__ import annotations

import uuid

from sqlalchemy import select

from app.core.pagination import paginate
from app.models.cluster import Cluster
from app.models.enums import ClusterStatus
from app.models.project import Project
from app.repositories.base import BaseRepository


class ClusterRepository(BaseRepository):
    async def get(self, cluster_id: uuid.UUID) -> Cluster | None:
        cluster = await self.db.get(Cluster, cluster_id)
        if cluster is None or cluster.deleted_at is not None:
            return None
        return cluster

    async def list(
        self,
        *,
        status: ClusterStatus | None = None,
        unclaimed: bool = False,
        limit: int = 20,
        cursor: str | None = None,
    ) -> tuple[list[Cluster], str | None]:
        stmt = select(Cluster).where(Cluster.deleted_at.is_(None))
        if status is not None:
            stmt = stmt.where(Cluster.status == status)
        if unclaimed:
            # A cluster that already has a Project is not an "opportunity"
            # any more - it's been claimed. Same has-project exclusion
            # find_open_nearest_by_embedding already applies for matching
            # suggestions, reused here for the opportunities listing.
            has_project = select(Project.id).where(Project.cluster_id == Cluster.id, Project.deleted_at.is_(None))
            stmt = stmt.where(~has_project.exists())
        return await paginate(self.db, stmt, model=Cluster, limit=limit, cursor=cursor)

    async def create(self, *, title: str, description: str | None, theme_id: uuid.UUID | None) -> Cluster:
        cluster = Cluster(title=title, description=description, theme_id=theme_id)
        self.db.add(cluster)
        await self.db.flush()
        return cluster

    async def find_open_nearest_by_embedding(
        self, *, embedding: list[float], limit: int
    ) -> list[tuple[Cluster, float]]:
        """ACTIVE clusters with no project yet — candidates a completed
        Solution elsewhere might be replicable to. A ranked suggestion only;
        nothing here creates or links anything automatically. Returns
        (cluster, cosine_distance) pairs, nearest first."""
        has_project = select(Project.id).where(Project.cluster_id == Cluster.id, Project.deleted_at.is_(None))
        distance = Cluster.embedding.cosine_distance(embedding)
        stmt = (
            select(Cluster, distance)
            .where(
                Cluster.deleted_at.is_(None),
                Cluster.status == ClusterStatus.ACTIVE,
                Cluster.embedding.is_not(None),
                ~has_project.exists(),
            )
            .order_by(distance)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]
