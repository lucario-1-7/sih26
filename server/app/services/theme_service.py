import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.theme import Theme
from app.repositories.audit_repository import AuditRepository
from app.repositories.theme_repository import ThemeRepository
from app.schemas.theme import ThemeCreate, ThemeUpdate

NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Theme not found", "code": "NOT_FOUND"}
)


async def create_theme(db: AsyncSession, *, data: ThemeCreate, actor_id: uuid.UUID) -> Theme:
    theme = await ThemeRepository(db).create(name=data.name, description=data.description)
    await AuditRepository(db).log(
        user_id=actor_id, action="theme.create", entity_type="theme", entity_id=theme.id
    )
    await db.commit()
    return theme


async def get_theme(db: AsyncSession, theme_id: uuid.UUID) -> Theme:
    theme = await ThemeRepository(db).get(theme_id)
    if theme is None:
        raise NOT_FOUND
    return theme


async def list_themes(db: AsyncSession, *, limit: int, cursor: str | None) -> tuple[list[Theme], str | None]:
    return await ThemeRepository(db).list(limit=limit, cursor=cursor)


async def update_theme(
    db: AsyncSession, theme_id: uuid.UUID, *, data: ThemeUpdate, actor_id: uuid.UUID
) -> Theme:
    theme = await ThemeRepository(db).get(theme_id)
    if theme is None:
        raise NOT_FOUND
    if data.name is not None:
        theme.name = data.name
    if data.description is not None:
        theme.description = data.description
    await AuditRepository(db).log(
        user_id=actor_id, action="theme.update", entity_type="theme", entity_id=theme.id
    )
    await db.commit()
    await db.refresh(theme)  # onupdate=now() is server-computed — refresh before serializing
    return theme
