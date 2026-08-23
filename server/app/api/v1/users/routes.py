import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.dependencies import get_current_user
from app.core.rbac import require_role
from app.db.session import get_db
from app.models.enums import Role
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.pagination import PaginatedResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services import user_management_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse, summary="Get the current authenticated user")
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    summary="List users (Superadmin only)",
)
async def list_users(
    role: Role | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role(Role.SUPERADMIN)),
) -> PaginatedResponse[UserResponse]:
    users, next_cursor = await UserRepository(db).list(role=role, limit=limit, cursor=cursor)
    return PaginatedResponse(
        items=[UserResponse.model_validate(u) for u in users],
        next_cursor=next_cursor,
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Provision a staff login (Superadmin only) — government/university/industry/superadmin",
)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role(Role.SUPERADMIN)),
) -> UserResponse:
    user = await user_management_service.create_user(db, data=payload, actor=admin)
    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update role/domain/organization/active-status (Superadmin only)",
)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role(Role.SUPERADMIN)),
) -> UserResponse:
    user = await user_management_service.update_user(db, user_id, data=payload, actor=admin)
    return UserResponse.model_validate(user)
