import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import require_role
from app.db.session import get_db
from app.models.enums import OrganizationType, Role
from app.models.user import User
from app.repositories.consortium_repository import ConsortiumRepository
from app.schemas.matching import (
    ConsortiumMemberResponse,
    ConsortiumRequest,
    ConsortiumResponse,
    MatchResult,
    OrganizationCreate,
    OrganizationResponse,
)
from app.schemas.pagination import PaginatedResponse
from app.services import matching_service
from app.services.job_queue import enqueue_consortium_suggestion

router = APIRouter(prefix="/matching", tags=["matching"])


@router.post(
    "/organizations",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a university/industry organization as a matching candidate (Superadmin-managed)",
)
async def create_organization(
    payload: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.SUPERADMIN)),
) -> OrganizationResponse:
    org = await matching_service.create_organization(db, data=payload, actor_id=user.id)
    return OrganizationResponse.model_validate(org)


@router.get(
    "/organizations", response_model=PaginatedResponse[OrganizationResponse], summary="List organizations"
)
async def list_organizations(
    type: OrganizationType | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[OrganizationResponse]:
    orgs, next_cursor = await matching_service.list_organizations(db, type=type, limit=limit, cursor=cursor)
    return PaginatedResponse(
        items=[OrganizationResponse.model_validate(o) for o in orgs],
        next_cursor=next_cursor,
    )


@router.get(
    "/clusters/{cluster_id}",
    response_model=list[MatchResult],
    summary="Rank organizations for a cluster by semantic + domain-tag match (explainable, not a guarantee)",
)
async def match_cluster(
    cluster_id: uuid.UUID,
    org_type: OrganizationType | None = Query(default=None, alias="type"),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(Role.VALIDATOR, Role.COORDINATOR, Role.SUPERADMIN)),
) -> list[MatchResult]:
    return await matching_service.rank_matches_for_cluster(db, cluster_id=cluster_id, org_type=org_type)


@router.post(
    "/projects/{project_id}/consortium",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Queue consortium formation suggestion for a project (ML ranks; server owns persistence)",
)
async def request_consortium(
    project_id: uuid.UUID,
    payload: ConsortiumRequest,
    _user: User = Depends(require_role(Role.COORDINATOR, Role.FACULTY, Role.SUPERADMIN)),
) -> dict:
    await enqueue_consortium_suggestion(str(project_id), payload.team_size)
    return {"detail": "Consortium suggestion queued"}


@router.get(
    "/projects/{project_id}/consortium",
    response_model=ConsortiumResponse | None,
    summary="Get the (proposed or confirmed) consortium for a project, if generated",
)
async def get_consortium(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ConsortiumResponse | None:
    consortium = await ConsortiumRepository(db).get_by_project(project_id)
    return ConsortiumResponse.model_validate(consortium) if consortium else None


@router.get(
    "/consortiums/{consortium_id}/members",
    response_model=list[ConsortiumMemberResponse],
    summary="List consortium members with match score and rationale",
)
async def list_consortium_members(
    consortium_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[ConsortiumMemberResponse]:
    members = await ConsortiumRepository(db).list_members(consortium_id)
    return [ConsortiumMemberResponse.model_validate(m) for m in members]


@router.patch(
    "/consortiums/{consortium_id}/confirm",
    response_model=ConsortiumResponse,
    summary="Coordinator/Faculty confirms a proposed consortium (human decision, auditable)",
)
async def confirm_consortium(
    consortium_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.COORDINATOR, Role.FACULTY, Role.SUPERADMIN)),
) -> ConsortiumResponse:
    consortium = await matching_service.confirm_consortium(db, consortium_id, actor_id=user.id)
    return ConsortiumResponse.model_validate(consortium)
