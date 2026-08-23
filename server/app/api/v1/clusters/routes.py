import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import require_role
from app.db.session import get_db
from app.models.enums import ClusterStatus, Role
from app.models.user import User
from app.schemas.cluster import ClusterCreate, ClusterResponse, ClusterUpdate
from app.schemas.pagination import PaginatedResponse
from app.services import cluster_service

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.post(
    "", response_model=ClusterResponse, status_code=status.HTTP_201_CREATED, summary="Create a cluster"
)
async def create_cluster(
    payload: ClusterCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.VALIDATOR, Role.SUPERADMIN)),
) -> ClusterResponse:
    cluster = await cluster_service.create_cluster(db, data=payload, actor_id=user.id)
    return ClusterResponse.model_validate(cluster)


@router.get("", response_model=PaginatedResponse[ClusterResponse], summary="List clusters")
async def list_clusters(
    status_filter: ClusterStatus | None = Query(default=None, alias="status"),
    unclaimed: bool = Query(
        default=False, description="Only clusters with no Project yet - the actual 'opportunities' feed."
    ),
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ClusterResponse]:
    clusters, next_cursor = await cluster_service.list_clusters(
        db, status_filter=status_filter, unclaimed=unclaimed, limit=limit, cursor=cursor
    )
    return PaginatedResponse(
        items=[ClusterResponse.model_validate(c) for c in clusters],
        next_cursor=next_cursor,
    )


@router.get("/{cluster_id}", response_model=ClusterResponse, summary="Get a cluster by id")
async def get_cluster(cluster_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ClusterResponse:
    cluster = await cluster_service.get_cluster(db, cluster_id)
    return ClusterResponse.model_validate(cluster)


@router.patch("/{cluster_id}", response_model=ClusterResponse, summary="Update a cluster")
async def update_cluster(
    cluster_id: uuid.UUID,
    payload: ClusterUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.VALIDATOR, Role.SUPERADMIN)),
) -> ClusterResponse:
    cluster = await cluster_service.update_cluster(db, cluster_id, data=payload, actor_id=user.id)
    return ClusterResponse.model_validate(cluster)
