from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.theme import Theme
from app.repositories.base import BaseRepository


class ThemeRepository(BaseRepository):
    async def get(self, theme_id: uuid.UUID) -> Theme | None:
        theme = await self.db.get(Theme, theme_id)
        if theme is None or theme.deleted_at is not None:
            return None
        return theme

    async def list(self, *, limit: int = 20, offset: int = 0) -> list[Theme]:
        stmt = (
            select(Theme)
            .where(Theme.deleted_at.is_(None))
            .order_by(Theme.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, *, name: str, description: str | None) -> Theme:
        theme = Theme(name=name, description=description)
        self.db.add(theme)
        await self.db.flush()
        return theme
