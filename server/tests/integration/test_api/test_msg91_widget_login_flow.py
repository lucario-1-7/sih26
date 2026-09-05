"""End-to-end (through real HTTP routes + real DB, mocked MSG91 network) for
the client-driven MSG91 OTP Widget login: POST /auth/customer/msg91/verify.
"""

import httpx
import pytest

from app.core.config import get_settings
from app.services import otp_msg91


def _configure_auth_key(monkeypatch, auth_key="test-account-key"):
    monkeypatch.setenv("MSG91_AUTH_KEY", auth_key)
    get_settings.cache_clear()


def _patch_client(monkeypatch, handler):
    monkeypatch.setattr(
        otp_msg91, "_client", lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://mock")
    )


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    yield
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_widget_login_round_trip_issues_a_normal_sociosolve_session(client, monkeypatch):
    _configure_auth_key(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"type": "success", "message": "919876522001"})

    _patch_client(monkeypatch, handler)

    resp = await client.post("/api/v1/auth/customer/msg91/verify", json={"access_token": "real-widget-token"})
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens and "refresh_token" in tokens

    resp = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["phone"] == "+919876522001"
    assert body["role"] == "citizen"


@pytest.mark.asyncio
async def test_second_login_resolves_the_same_customer_not_a_duplicate(client, monkeypatch):
    _configure_auth_key(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"type": "success", "message": "919876522002"})

    _patch_client(monkeypatch, handler)

    resp1 = await client.post("/api/v1/auth/customer/msg91/verify", json={"access_token": "token-a"})
    resp2 = await client.post("/api/v1/auth/customer/msg91/verify", json={"access_token": "token-b"})
    assert resp1.status_code == 200 and resp2.status_code == 200

    id1 = (
        await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {resp1.json()['access_token']}"})
    ).json()["id"]
    id2 = (
        await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {resp2.json()['access_token']}"})
    ).json()["id"]
    assert id1 == id2


@pytest.mark.asyncio
async def test_invalid_access_token_is_rejected_with_401_not_500(client, monkeypatch):
    _configure_auth_key(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"type": "error", "message": "invalid access-token"})

    _patch_client(monkeypatch, handler)

    resp = await client.post("/api/v1/auth/customer/msg91/verify", json={"access_token": "forged-token"})
    assert resp.status_code == 401
    assert resp.json()["code"] == "INVALID_ACCESS_TOKEN"


@pytest.mark.asyncio
async def test_provider_outage_is_503_not_401(client, monkeypatch):
    """A down/misconfigured MSG91 must never be reported as an invalid
    credential — the client needs to know to retry, not that they typed
    something wrong."""
    _configure_auth_key(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out", request=request)

    _patch_client(monkeypatch, handler)

    resp = await client.post("/api/v1/auth/customer/msg91/verify", json={"access_token": "any-token"})
    assert resp.status_code == 503
    assert resp.json()["code"] == "OTP_DELIVERY_UNAVAILABLE"


@pytest.mark.asyncio
async def test_missing_msg91_auth_key_is_503_not_a_crash(client, monkeypatch):
    monkeypatch.setenv("MSG91_AUTH_KEY", "")
    get_settings.cache_clear()

    resp = await client.post("/api/v1/auth/customer/msg91/verify", json={"access_token": "any-token"})
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_empty_body_is_rejected_with_422(client):
    resp = await client.post("/api/v1/auth/customer/msg91/verify", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_no_secrets_or_tokens_appear_in_the_error_response(client, monkeypatch, caplog):
    _configure_auth_key(monkeypatch, auth_key="super-secret-should-never-leak")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"type": "error", "message": "bad authkey"})

    _patch_client(monkeypatch, handler)

    resp = await client.post("/api/v1/auth/customer/msg91/verify", json={"access_token": "any-token"})
    assert resp.status_code == 503
    assert "super-secret-should-never-leak" not in resp.text
