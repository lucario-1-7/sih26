import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cluster import Cluster
from app.models.enums import ClusterStatus
from app.repositories.audit_repository import AuditRepository
from app.repositories.cluster_repository import ClusterRepository
from app.schemas.cluster import ClusterCreate, ClusterUpdate

NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Cluster not found", "code": "NOT_FOUND"}
)


async def create_cluster(db: AsyncSession, *, data: ClusterCreate, actor_id: uuid.UUID) -> Cluster:
    cluster = await ClusterRepository(db).create(
        title=data.title, description=data.description, theme_id=data.theme_id
    )
    await AuditRepository(db).log(
        user_id=actor_id, action="cluster.create", entity_type="cluster", entity_id=cluster.id
    )
    await db.commit()
    return cluster


async def get_cluster(db: AsyncSession, cluster_id: uuid.UUID) -> Cluster:
    cluster = await ClusterRepository(db).get(cluster_id)
    if cluster is None:
        raise NOT_FOUND
    return cluster


async def list_clusters(
    db: AsyncSession, *, status_filter: ClusterStatus | None, limit: int, offset: int
) -> list[Cluster]:
    return await ClusterRepository(db).list(status=status_filter, limit=limit, offset=offset)


async def update_cluster(
    db: AsyncSession, cluster_id: uuid.UUID, *, data: ClusterUpdate, actor_id: uuid.UUID
) -> Cluster:
    cluster = await ClusterRepository(db).get(cluster_id)
    if cluster is None:
        raise NOT_FOUND
    if data.title is not None:
        cluster.title = data.title
    if data.description is not None:
        cluster.description = data.description
    if data.theme_id is not None:
        cluster.theme_id = data.theme_id
    if data.status is not None:
        cluster.status = data.status
    await AuditRepository(db).log(
        user_id=actor_id, action="cluster.update", entity_type="cluster", entity_id=cluster.id
    )
    await db.commit()
    return cluster
