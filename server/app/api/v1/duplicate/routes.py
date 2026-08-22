import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import require_role
from app.db.session import get_db
from app.models.enums import Role
from app.models.user import User
from app.schemas.duplicate import (
    DuplicateCandidateResponse,
    DuplicateDecisionCreate,
    DuplicateDecisionResponse,
)
from app.services import duplicate_service

router = APIRouter(prefix="/duplicate", tags=["duplicate"])


@router.get(
    "/challenges/{challenge_id}/candidates",
    response_model=list[DuplicateCandidateResponse],
    summary="List ML-suggested duplicate candidates for a challenge (evidence only, not a decision)",
)
async def list_candidates(
    challenge_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(Role.VALIDATOR, Role.SUPERADMIN)),
) -> list[DuplicateCandidateResponse]:
    candidates = await duplicate_service.list_candidates(db, challenge_id)
    return [DuplicateCandidateResponse.model_validate(c) for c in candidates]


@router.post(
    "/decisions",
    response_model=DuplicateDecisionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a human DUPLICATE / NOT_DUPLICATE decision (auditable, never automatic)",
)
async def create_decision(
    payload: DuplicateDecisionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.VALIDATOR)),
) -> DuplicateDecisionResponse:
    decision = await duplicate_service.decide(db, data=payload, reviewer_id=user.id)
    return DuplicateDecisionResponse.model_validate(decision)
