import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.enums import AdministrativeLevel
from app.repositories.administrative_area_repository import AdministrativeAreaRepository
from app.schemas.administrative_area import AdministrativeAreaResponse
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/administrative-areas", tags=["administrative-areas"])


@router.get(
    "",
    response_model=PaginatedResponse[AdministrativeAreaResponse],
    summary="List administrative areas — used to resolve a citizen's location to a valid area_id",
)
async def list_administrative_areas(
    level: AdministrativeLevel | None = None,
    parent_id: uuid.UUID | None = None,
    search: str | None = Query(default=None, max_length=200),
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[AdministrativeAreaResponse]:
    areas, next_cursor = await AdministrativeAreaRepository(db).list(
        level=level, parent_id=parent_id, search=search, limit=limit, cursor=cursor
    )
    return PaginatedResponse(
        items=[AdministrativeAreaResponse.model_validate(a) for a in areas],
        next_cursor=next_cursor,
    )
