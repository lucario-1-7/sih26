"""PRESENTATION-ONLY demo/bypass login — POST /auth/demo/login.

Covers: off by default, works when explicitly enabled, force-disabled in
production regardless of DEMO_MODE, real JWT/RBAC (not a fabricated
session), and that normal OTP auth is completely unaffected either way.
"""

import uuid

import jwt
import pytest
from sqlalchemy import select

from app.core.config import get_settings
from app.models.enums import Role
from app.models.user import User


def _enable_demo_mode(monkeypatch, *, environment="development"):
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("ENVIRONMENT", environment)
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    yield
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_demo_login_is_404_by_default(client):
    # The conftest autouse fixture forces DEMO_MODE=false for every test
    # regardless of Settings' own default or what's in the real .env.
    resp = await client.post("/api/v1/auth/demo/login", json={"persona": "citizen"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_demo_login_issues_a_real_session_when_enabled(client, monkeypatch, db):
    _enable_demo_mode(monkeypatch)

    resp = await client.post("/api/v1/auth/demo/login", json={"persona": "citizen"})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body and "refresh_token" in body

    # It's a REAL JWT with the REAL claims a normal login would carry.
    settings = get_settings()
    claims = jwt.decode(body["access_token"], settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert claims["role"] == "citizen"

    # And a REAL, persisted user row — not fabricated in-memory state.
    result = await db.execute(select(User).where(User.phone == "+910000000001"))
    user = result.scalar_one()
    assert user.role == Role.CITIZEN

    # The protected endpoint actually accepts this token.
    me = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["phone"] == "+910000000001"


@pytest.mark.asyncio
async def test_demo_login_covers_every_organization_persona(client, monkeypatch):
    _enable_demo_mode(monkeypatch)

    expected_roles = {
        "citizen": "citizen",
        "government_validator": "validator",
        "government_field_assistant": "field_assistant",
        "university_coordinator": "coordinator",
        "industry": "industry",
        "superadmin": "superadmin",
    }
    settings = get_settings()
    for persona, role in expected_roles.items():
        resp = await client.post("/api/v1/auth/demo/login", json={"persona": persona})
        assert resp.status_code == 200, persona
        claims = jwt.decode(
            resp.json()["access_token"], settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        assert claims["role"] == role, persona


@pytest.mark.asyncio
async def test_demo_login_rejects_an_unknown_persona(client, monkeypatch):
    _enable_demo_mode(monkeypatch)
    resp = await client.post("/api/v1/auth/demo/login", json={"persona": "not-a-real-persona"})
    assert resp.status_code == 422
    assert resp.json()["code"] == "UNKNOWN_DEMO_PERSONA"


@pytest.mark.asyncio
async def test_demo_mode_cannot_activate_in_production_even_if_set(client, monkeypatch):
    _enable_demo_mode(monkeypatch, environment="production")
    resp = await client.post("/api/v1/auth/demo/login", json={"persona": "citizen"})
    assert resp.status_code == 404


def test_settings_force_disables_demo_mode_in_production(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("ENVIRONMENT", "production")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.ENVIRONMENT == "production"
    assert settings.DEMO_MODE is False


def test_settings_allow_demo_mode_outside_production(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("ENVIRONMENT", "development")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.DEMO_MODE is True


@pytest.mark.asyncio
async def test_normal_otp_login_route_is_unaffected_by_demo_mode_being_off(client):
    # Sanity: the demo endpoint's existence doesn't change the real OTP
    # route's behavior at all — still 202 Accepted for a well-formed request
    # against the dev/console fallback (DEMO_MODE and MSG91 vars are both
    # cleared by the autouse conftest fixture for this test).
    phone = f"+91{uuid.uuid4().int % 10**10:010d}"
    resp = await client.post("/api/v1/auth/otp/request", json={"phone": phone})
    assert resp.status_code == 202
