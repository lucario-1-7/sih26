import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cluster import Cluster
from app.models.enums import ClusterStatus
from app.repositories.audit_repository import AuditRepository
from app.repositories.cluster_repository import ClusterRepository
from app.schemas.cluster import ClusterCreate, ClusterUpdate
from app.services.job_queue import enqueue_cluster_embedding_generation

NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Cluster not found", "code": "NOT_FOUND"}
)

logger = logging.getLogger("app.clusters")


async def _enqueue_embedding_job(cluster_id: uuid.UUID) -> None:
    # Enqueued only after the transaction commits, so the worker can see the
    # row. The cluster was already durably persisted — a briefly unreachable
    # Redis must not fail the request; the embedding is simply generated later.
    try:
        await enqueue_cluster_embedding_generation(str(cluster_id))
    except Exception:
        logger.error(
            "Failed to enqueue embedding job for cluster %s; it will remain unembedded "
            "until reprocessed.",
            cluster_id,
            exc_info=True,
        )


async def create_cluster(db: AsyncSession, *, data: ClusterCreate, actor_id: uuid.UUID) -> Cluster:
    cluster = await ClusterRepository(db).create(
        title=data.title, description=data.description, theme_id=data.theme_id
    )
    await AuditRepository(db).log(
        user_id=actor_id, action="cluster.create", entity_type="cluster", entity_id=cluster.id
    )
    await db.commit()
    await _enqueue_embedding_job(cluster.id)
    return cluster


async def get_cluster(db: AsyncSession, cluster_id: uuid.UUID) -> Cluster:
    cluster = await ClusterRepository(db).get(cluster_id)
    if cluster is None:
        raise NOT_FOUND
    return cluster


async def list_clusters(
    db: AsyncSession,
    *,
    status_filter: ClusterStatus | None,
    unclaimed: bool,
    limit: int,
    cursor: str | None,
) -> tuple[list[Cluster], str | None]:
    return await ClusterRepository(db).list(status=status_filter, unclaimed=unclaimed, limit=limit, cursor=cursor)


async def update_cluster(
    db: AsyncSession, cluster_id: uuid.UUID, *, data: ClusterUpdate, actor_id: uuid.UUID
) -> Cluster:
    cluster = await ClusterRepository(db).get(cluster_id)
    if cluster is None:
        raise NOT_FOUND
    content_changed = (data.title is not None and data.title != cluster.title) or (
        data.description is not None and data.description != cluster.description
    )
    if data.title is not None:
        cluster.title = data.title
    if data.description is not None:
        cluster.description = data.description
    if data.theme_id is not None:
        cluster.theme_id = data.theme_id
    if data.status is not None:
        cluster.status = data.status
    if content_changed:
        # Invalidate the stale embedding — the background job recomputes it
        # rather than a GET lazily computing and persisting it.
        cluster.embedding = None
    await AuditRepository(db).log(
        user_id=actor_id, action="cluster.update", entity_type="cluster", entity_id=cluster.id
    )
    await db.commit()
    await db.refresh(cluster)  # onupdate=now() is server-computed — refresh before serializing
    if content_changed:
        await _enqueue_embedding_job(cluster.id)
    return cluster
