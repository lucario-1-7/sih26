import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import require_role
from app.db.session import get_db
from app.models.enums import Role
from app.models.user import User
from app.schemas.collaboration import (
    CollaborationCreate,
    CollaborationResponse,
    CollaborationStatusUpdate,
    CommitmentCreate,
    CommitmentResponse,
    CommitmentStatusUpdate,
)
from app.schemas.pagination import PaginatedResponse
from app.services import collaboration_service

router = APIRouter(prefix="/collaborations", tags=["collaboration"])

_UNIVERSITY_OR_ADMIN = (Role.COORDINATOR, Role.FACULTY, Role.SUPERADMIN)


@router.post(
    "",
    response_model=CollaborationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Industry expresses interest in a project (starts at INTERESTED)",
)
async def create_collaboration(
    payload: CollaborationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.INDUSTRY)),
) -> CollaborationResponse:
    collaboration = await collaboration_service.create_collaboration(db, data=payload, actor=user)
    return CollaborationResponse.model_validate(collaboration)


@router.get(
    "",
    response_model=PaginatedResponse[CollaborationResponse],
    summary="List collaborations — by project (university/gov view) or the caller's own organization (industry view)",
)
async def list_collaborations(
    project_id: uuid.UUID | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.INDUSTRY, Role.COORDINATOR, Role.FACULTY, Role.VALIDATOR, Role.SUPERADMIN)),
) -> PaginatedResponse[CollaborationResponse]:
    if project_id is not None:
        collaborations, next_cursor = await collaboration_service.list_collaborations_for_project(
            db, project_id, limit=limit, cursor=cursor
        )
    else:
        collaborations, next_cursor = await collaboration_service.list_collaborations_for_my_organization(
            db, actor=user, limit=limit, cursor=cursor
        )
    return PaginatedResponse(
        items=[CollaborationResponse.model_validate(c) for c in collaborations], next_cursor=next_cursor
    )


@router.patch(
    "/{collaboration_id}/status",
    response_model=CollaborationResponse,
    summary="Advance a collaboration's lifecycle (Industry proposes; University accepts/rejects/activates/completes)",
)
async def update_collaboration_status(
    collaboration_id: uuid.UUID,
    payload: CollaborationStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.INDUSTRY, *_UNIVERSITY_OR_ADMIN)),
) -> CollaborationResponse:
    collaboration = await collaboration_service.update_collaboration_status(
        db, collaboration_id, data=payload, actor=user
    )
    return CollaborationResponse.model_validate(collaboration)


@router.post(
    "/{collaboration_id}/commitments",
    response_model=CommitmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Industry proposes a funding/mentoring/resource commitment",
)
async def create_commitment(
    collaboration_id: uuid.UUID,
    payload: CommitmentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.INDUSTRY)),
) -> CommitmentResponse:
    commitment = await collaboration_service.create_commitment(db, collaboration_id, data=payload, actor=user)
    return CommitmentResponse.model_validate(commitment)


@router.get(
    "/{collaboration_id}/commitments",
    response_model=PaginatedResponse[CommitmentResponse],
    summary="List a collaboration's commitments",
)
async def list_commitments(
    collaboration_id: uuid.UUID,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.INDUSTRY, *_UNIVERSITY_OR_ADMIN)),
) -> PaginatedResponse[CommitmentResponse]:
    commitments, next_cursor = await collaboration_service.list_commitments(
        db, collaboration_id, limit=limit, cursor=cursor
    )
    return PaginatedResponse(
        items=[CommitmentResponse.model_validate(c) for c in commitments], next_cursor=next_cursor
    )


@router.patch(
    "/{collaboration_id}/commitments/{commitment_id}/status",
    response_model=CommitmentResponse,
    summary="University reviews a commitment (accept/fulfill/reject)",
)
async def update_commitment_status(
    collaboration_id: uuid.UUID,
    commitment_id: uuid.UUID,
    payload: CommitmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(*_UNIVERSITY_OR_ADMIN)),
) -> CommitmentResponse:
    commitment = await collaboration_service.update_commitment_status(
        db,
        collaboration_id,
        commitment_id,
        new_status=payload.status,
        evidence=payload.evidence,
        actor=user,
    )
    return CommitmentResponse.model_validate(commitment)
