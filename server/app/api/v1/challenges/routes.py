import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import require_role
from app.db.session import get_db
from app.models.enums import ChallengeStatus, Role
from app.models.user import User
from app.schemas.challenge import ChallengeCreate, ChallengeResponse, ChallengeUpdate
from app.schemas.pagination import PaginatedResponse
from app.services import challenge_service

router = APIRouter(prefix="/challenges", tags=["challenges"])


@router.post(
    "", response_model=ChallengeResponse, status_code=status.HTTP_201_CREATED, summary="Submit a challenge"
)
async def create_challenge(
    payload: ChallengeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.CITIZEN, Role.FIELD_ASSISTANT)),
) -> ChallengeResponse:
    challenge = await challenge_service.create_challenge(db, data=payload, actor=user)
    return ChallengeResponse.model_validate(challenge)


@router.get("", response_model=PaginatedResponse[ChallengeResponse], summary="List challenges")
async def list_challenges(
    status_filter: ChallengeStatus | None = Query(default=None, alias="status"),
    submitted_by_id: uuid.UUID | None = None,
    cluster_id: uuid.UUID | None = None,
    unclustered: bool = Query(default=False),
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ChallengeResponse]:
    challenges, next_cursor = await challenge_service.list_challenges(
        db,
        status_filter=status_filter,
        submitted_by_id=submitted_by_id,
        cluster_id=cluster_id,
        unclustered=unclustered,
        limit=limit,
        cursor=cursor,
    )
    return PaginatedResponse(
        items=[ChallengeResponse.model_validate(c) for c in challenges],
        next_cursor=next_cursor,
    )


@router.get("/{challenge_id}", response_model=ChallengeResponse, summary="Get a challenge by id")
async def get_challenge(challenge_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ChallengeResponse:
    challenge = await challenge_service.get_challenge(db, challenge_id)
    return ChallengeResponse.model_validate(challenge)


@router.patch("/{challenge_id}", response_model=ChallengeResponse, summary="Update a challenge")
async def update_challenge(
    challenge_id: uuid.UUID,
    payload: ChallengeUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.CITIZEN, Role.FIELD_ASSISTANT, Role.VALIDATOR, Role.SUPERADMIN)),
) -> ChallengeResponse:
    challenge = await challenge_service.update_challenge(db, challenge_id, data=payload, actor=user)
    return ChallengeResponse.model_validate(challenge)
