import os
import uuid
from pathlib import Path

from dotenv import dotenv_values

# Redirect the app's DATABASE_URL to TEST_DATABASE_URL *before* app.db.session
# is imported anywhere (it creates its engine at import time) — this is what
# actually isolates integration tests from the sih26_dev database. Falls back
# to DATABASE_URL (today's behavior) if TEST_DATABASE_URL isn't configured, so
# this doesn't break a dev setup that hasn't added it yet.
_repo_root_env = Path(__file__).resolve().parents[2] / ".env"
_env_values = {**dotenv_values(_repo_root_env), **os.environ}
_test_db_url = _env_values.get("TEST_DATABASE_URL")
if _test_db_url:
    os.environ["DATABASE_URL"] = _test_db_url

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenType, create_token
from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.administrative_area import AdministrativeArea
from app.models.enums import AdministrativeLevel, Role
from app.models.user import User


@pytest_asyncio.fixture
async def db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def administrative_area(db: AsyncSession) -> AdministrativeArea:
    area = AdministrativeArea(name=f"Test State {uuid.uuid4().hex[:8]}", level=AdministrativeLevel.STATE)
    db.add(area)
    await db.commit()
    await db.refresh(area)
    return area


async def _make_user(db: AsyncSession, role: Role) -> User:
    user = User(phone=f"+91{uuid.uuid4().int % 10**10:010d}", name=f"Test {role.value}", role=role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def citizen_user(db: AsyncSession) -> User:
    return await _make_user(db, Role.CITIZEN)


@pytest_asyncio.fixture
async def officer_user(db: AsyncSession) -> User:
    return await _make_user(db, Role.OFFICER)


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession) -> User:
    return await _make_user(db, Role.ADMIN)


def auth_headers(user: User) -> dict:
    token, _ = create_token(
        user_id=user.id, role=user.role.value, token_type=TokenType.ACCESS, expires_minutes=15
    )
    return {"Authorization": f"Bearer {token}"}
