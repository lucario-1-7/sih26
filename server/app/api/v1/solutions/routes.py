import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import require_role
from app.db.session import get_db
from app.models.enums import Role
from app.models.user import User
from app.schemas.pagination import PaginatedResponse
from app.schemas.solution import ReplicationCandidateResponse, SolutionCreate, SolutionResponse, SolutionUpdate
from app.services import solution_service

router = APIRouter(prefix="/solutions", tags=["solutions"])


@router.post(
    "", response_model=SolutionResponse, status_code=status.HTTP_201_CREATED, summary="Create a solution"
)
async def create_solution(
    payload: SolutionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.FACULTY, Role.COORDINATOR, Role.SUPERADMIN)),
) -> SolutionResponse:
    solution = await solution_service.create_solution(db, data=payload, actor=user)
    return SolutionResponse.model_validate(solution)


@router.get("", response_model=PaginatedResponse[SolutionResponse], summary="List solutions")
async def list_solutions(
    project_id: uuid.UUID | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[SolutionResponse]:
    solutions, next_cursor = await solution_service.list_solutions(
        db, project_id=project_id, limit=limit, cursor=cursor
    )
    return PaginatedResponse(
        items=[SolutionResponse.model_validate(s) for s in solutions],
        next_cursor=next_cursor,
    )


@router.get("/{solution_id}", response_model=SolutionResponse, summary="Get a solution by id")
async def get_solution(solution_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> SolutionResponse:
    solution = await solution_service.get_solution(db, solution_id)
    return SolutionResponse.model_validate(solution)


@router.patch(
    "/{solution_id}",
    response_model=SolutionResponse,
    summary="Update a solution's content or publish it (status -> published)",
)
async def update_solution(
    solution_id: uuid.UUID,
    payload: SolutionUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.FACULTY, Role.COORDINATOR, Role.SUPERADMIN)),
) -> SolutionResponse:
    solution = await solution_service.update_solution(db, solution_id, data=payload, actor=user)
    return SolutionResponse.model_validate(solution)


@router.get(
    "/{solution_id}/replication-candidates",
    response_model=list[ReplicationCandidateResponse],
    summary="Ranked open clusters this solution might be replicable to (recommendation only — no auto action)",
)
async def get_replication_candidates(
    solution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(Role.COORDINATOR, Role.FACULTY, Role.VALIDATOR, Role.SUPERADMIN)),
) -> list[ReplicationCandidateResponse]:
    return await solution_service.get_replication_candidates(db, solution_id)
