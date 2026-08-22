import uuid

import pytest

from app.repositories.theme_repository import ThemeRepository


@pytest.mark.asyncio
async def test_create_and_get_theme(db):
    repo = ThemeRepository(db)
    name = f"Road Infrastructure Test {uuid.uuid4().hex[:8]}"
    theme = await repo.create(name=name, description="Roads and drainage")
    await db.commit()

    fetched = await repo.get(theme.id)
    assert fetched is not None
    assert fetched.name == name


@pytest.mark.asyncio
async def test_get_missing_theme_returns_none(db):
    import uuid

    repo = ThemeRepository(db)
    assert await repo.get(uuid.uuid4()) is None
