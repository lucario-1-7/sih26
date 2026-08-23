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

from app.core.config import get_settings
from app.core.security import TokenType, create_token
from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.administrative_area import AdministrativeArea
from app.models.enums import AdministrativeLevel, Domain, OrganizationType, Role
from app.models.organization import Organization
from app.models.user import User


@pytest.fixture(autouse=True)
def _no_real_msg91_credentials_by_default(monkeypatch):
    """Tests must never depend on whatever MSG91 credentials happen to be in
    the developer's real .env — the whole test suite previously "worked"
    only because the real .env had no MSG91_TOKEN_AUTH configured yet. Now
    that this repo has real production MSG91 credentials configured for the
    live app, every OTP-related test would otherwise silently switch from
    the local dev-fallback/mocked path onto real, network-dependent calls
    to MSG91's live API (observed: real sendOtpMobile calls, rejected by
    MSG91 as IPBlocked, during a plain `pytest` run).

    monkeypatch.setenv(key, "") — not delenv — because pydantic-settings
    reads the real .env file directly; delenv only touches os.environ and
    a real .env value would still leak through.

    The same applies to DEMO_MODE — a presentation deployment's real .env
    sets DEMO_MODE=true, and without this the "demo login is 404 by
    default" test would silently start failing (or worse, silently start
    passing for the wrong reason) whenever run against that .env.

    Tests that specifically exercise the MSG91-configured or demo-mode
    path (e.g. tests/unit/test_services/test_otp_msg91.py,
    tests/integration/test_api/test_msg91_widget_login_flow.py,
    tests/integration/test_api/test_demo_login.py) set these explicitly
    via their own monkeypatch calls within the test body, which run after
    this fixture and take precedence for that test.
    """
    for key in ("MSG91_WIDGET_ID", "MSG91_TOKEN_AUTH", "MSG91_AUTH_KEY"):
        monkeypatch.setenv(key, "")
    monkeypatch.setenv("DEMO_MODE", "false")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


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


async def _make_user(
    db: AsyncSession, role: Role, domain: Domain, organization_id: uuid.UUID | None = None
) -> User:
    user = User(
        phone=f"+91{uuid.uuid4().int % 10**10:010d}",
        name=f"Test {role.value}",
        role=role,
        domain=domain,
        organization_id=organization_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def citizen_user(db: AsyncSession) -> User:
    return await _make_user(db, Role.CITIZEN, Domain.CITIZEN)


@pytest_asyncio.fixture
async def field_assistant_user(db: AsyncSession) -> User:
    return await _make_user(db, Role.FIELD_ASSISTANT, Domain.GOVERNMENT)


@pytest_asyncio.fixture
async def validator_user(db: AsyncSession) -> User:
    return await _make_user(db, Role.VALIDATOR, Domain.GOVERNMENT)


@pytest_asyncio.fixture
async def superadmin_user(db: AsyncSession) -> User:
    return await _make_user(db, Role.SUPERADMIN, Domain.SUPERADMIN)


async def _make_organization(db: AsyncSession, type: OrganizationType) -> Organization:
    org = Organization(name=f"Test {type.value} Org {uuid.uuid4().hex[:8]}", type=type, domain_tags=[])
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@pytest_asyncio.fixture
async def university_org(db: AsyncSession) -> Organization:
    return await _make_organization(db, OrganizationType.UNIVERSITY)


@pytest_asyncio.fixture
async def industry_org(db: AsyncSession) -> Organization:
    return await _make_organization(db, OrganizationType.INDUSTRY)


@pytest_asyncio.fixture
async def coordinator_user(db: AsyncSession, university_org: Organization) -> User:
    return await _make_user(db, Role.COORDINATOR, Domain.UNIVERSITY, university_org.id)


@pytest_asyncio.fixture
async def faculty_user(db: AsyncSession, university_org: Organization) -> User:
    return await _make_user(db, Role.FACULTY, Domain.UNIVERSITY, university_org.id)


@pytest_asyncio.fixture
async def industry_user(db: AsyncSession, industry_org: Organization) -> User:
    return await _make_user(db, Role.INDUSTRY, Domain.INDUSTRY, industry_org.id)


def auth_headers(user: User) -> dict:
    token, _ = create_token(
        user_id=user.id, role=user.role.value, token_type=TokenType.ACCESS, expires_minutes=15
    )
    return {"Authorization": f"Bearer {token}"}
