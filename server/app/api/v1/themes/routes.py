import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import require_role
from app.db.session import get_db
from app.models.enums import Role
from app.models.user import User
from app.schemas.pagination import PaginatedResponse
from app.schemas.theme import ThemeCreate, ThemeResponse, ThemeUpdate
from app.services import theme_service

router = APIRouter(prefix="/themes", tags=["themes"])


@router.post(
    "", response_model=ThemeResponse, status_code=status.HTTP_201_CREATED, summary="Create a theme"
)
async def create_theme(
    payload: ThemeCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.VALIDATOR, Role.SUPERADMIN)),
) -> ThemeResponse:
    theme = await theme_service.create_theme(db, data=payload, actor_id=user.id)
    return ThemeResponse.model_validate(theme)


@router.get("", response_model=PaginatedResponse[ThemeResponse], summary="List themes")
async def list_themes(
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ThemeResponse]:
    themes, next_cursor = await theme_service.list_themes(db, limit=limit, cursor=cursor)
    return PaginatedResponse(
        items=[ThemeResponse.model_validate(t) for t in themes],
        next_cursor=next_cursor,
    )


@router.get("/{theme_id}", response_model=ThemeResponse, summary="Get a theme by id")
async def get_theme(theme_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ThemeResponse:
    theme = await theme_service.get_theme(db, theme_id)
    return ThemeResponse.model_validate(theme)


@router.patch("/{theme_id}", response_model=ThemeResponse, summary="Update a theme")
async def update_theme(
    theme_id: uuid.UUID,
    payload: ThemeUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.VALIDATOR, Role.SUPERADMIN)),
) -> ThemeResponse:
    theme = await theme_service.update_theme(db, theme_id, data=payload, actor_id=user.id)
    return ThemeResponse.model_validate(theme)
