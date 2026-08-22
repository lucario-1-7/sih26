from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.dependencies import get_current_user
from app.core.rbac import require_role
from app.db.session import get_db
from app.models.enums import Role
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.pagination import PaginatedResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse, summary="Get the current authenticated user")
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    summary="List users (admin only)",
)
async def list_users(
    role: Role | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role(Role.ADMIN)),
) -> PaginatedResponse[UserResponse]:
    users = await UserRepository(db).list(role=role, limit=limit, offset=offset)
    return PaginatedResponse(
        items=[UserResponse.model_validate(u) for u in users],
        next_cursor=str(offset + limit) if len(users) == limit else None,
    )
