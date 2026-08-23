import logging

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.services import otp_dev_store


@pytest.mark.asyncio
async def test_dev_otp_endpoint_returns_the_requested_code_in_development(client, monkeypatch):
    """Default test settings are ENVIRONMENT=development (see .env) — the
    endpoint should be mounted and return the same code the citizen would
    need to complete /auth/otp/verify."""
    phone = "+919812300001"
    resp = await client.post("/api/v1/auth/otp/request", json={"phone": phone})
    assert resp.status_code == 202

    resp = await client.get("/api/v1/auth/dev/otp", params={"phone": phone})
    assert resp.status_code == 200
    code = resp.json()["code"]

    # The retrieved code actually works — proves it's the real OTP, not a stub.
    resp = await client.post("/api/v1/auth/otp/verify", json={"phone": phone, "code": code})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_dev_otp_endpoint_404s_for_unknown_phone_in_development(client):
    resp = await client.get("/api/v1/auth/dev/otp", params={"phone": "+919812399999"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_dev_otp_route_is_not_mounted_when_environment_is_production(monkeypatch):
    """Rebuilds the FastAPI app with ENVIRONMENT=production and proves the
    dev route doesn't exist at all — not just that it 403s/404s, but that
    there is no such route registered on the app."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    get_settings.cache_clear()
    try:
        from app.main import create_app

        prod_app = create_app()

        dev_paths = [r.path for r in prod_app.routes if getattr(r, "path", "").startswith("/api/v1/auth/dev")]
        assert dev_paths == []

        transport = ASGITransport(app=prod_app)
        async with AsyncClient(transport=transport, base_url="http://test") as prod_client:
            resp = await prod_client.get("/api/v1/auth/dev/otp", params={"phone": "+919812300001"})
        assert resp.status_code == 404
    finally:
        get_settings.cache_clear()


def test_store_dev_otp_is_a_noop_outside_development(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    get_settings.cache_clear()
    try:
        otp_dev_store.store_dev_otp("+919812300002", "654321")
        assert otp_dev_store.get_dev_otp("+919812300002") is None
    finally:
        get_settings.cache_clear()


def test_get_dev_otp_returns_none_outside_development_even_if_stored_in_dev(monkeypatch):
    # Store while genuinely in development...
    get_settings.cache_clear()
    otp_dev_store.store_dev_otp("+919812300003", "111222")
    assert otp_dev_store.get_dev_otp("+919812300003") == "111222"

    # ...but a later read under production must never surface it.
    monkeypatch.setenv("ENVIRONMENT", "production")
    get_settings.cache_clear()
    try:
        assert otp_dev_store.get_dev_otp("+919812300003") is None
    finally:
        get_settings.cache_clear()


@pytest.mark.asyncio
async def test_request_otp_logs_the_plaintext_code_in_development(db, caplog):
    """Explicitly requested, narrowly-scoped exception to "no plaintext
    OTPs": in development only, so the code is readable straight from
    `docker compose logs -f server`. See otp_sender.ConsoleOtpSender."""
    from app.services import auth_service

    get_settings.cache_clear()  # ensure a genuinely fresh "development" read
    caplog.set_level(logging.DEBUG)
    phone = "+919812300004"

    await auth_service.request_otp(db, phone=phone, ip_address=None)

    code = otp_dev_store.get_dev_otp(phone)
    assert code is not None
    assert any(code in record.getMessage() for record in caplog.records)


@pytest.mark.asyncio
async def test_request_otp_never_logs_the_plaintext_code_in_production(db, caplog, monkeypatch):
    """In production, OTP delivery goes through MSG91 (see test_otp_msg91.py
    for the sender's own unit tests) — this test only asserts the
    no-plaintext-logging invariant, against a mocked MSG91 call so it never
    touches the real network."""
    import httpx

    from app.services import auth_service, otp_msg91

    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("MSG91_WIDGET_ID", "test-widget-id")
    monkeypatch.setenv("MSG91_TOKEN_AUTH", "test-token-auth-must-never-appear-in-logs")
    get_settings.cache_clear()
    import app.services.otp_sender as otp_sender_module

    otp_sender_module._sender = None
    try:

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"type": "success", "message": "req-id-123"})

        monkeypatch.setattr(
            otp_msg91,
            "_client",
            lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://mock"),
        )

        caplog.set_level(logging.DEBUG)
        phone = "+919812300005"

        await auth_service.request_otp(db, phone=phone, ip_address=None)

        # otp_dev_store itself is also a no-op outside development — the
        # code isn't retrievable through it either (moot here anyway: MSG91
        # generated the code itself, we never had it).
        assert otp_dev_store.get_dev_otp(phone) is None

        for record in caplog.records:
            message = record.getMessage()
            assert "otp=" not in message
            assert "test-token-auth-must-never-appear-in-logs" not in message
            assert len(message) < 200  # sanity: no accidental huge dump containing the code

    finally:
        get_settings.cache_clear()
        otp_sender_module._sender = None


@pytest.mark.asyncio
async def test_no_access_or_refresh_tokens_are_logged(client, caplog):
    caplog.set_level(logging.DEBUG)
    phone = "+919812300006"

    resp = await client.post("/api/v1/auth/otp/request", json={"phone": phone})
    assert resp.status_code == 202
    code = otp_dev_store.get_dev_otp(phone)
    assert code is not None

    resp = await client.post("/api/v1/auth/otp/verify", json={"phone": phone, "code": code})
    assert resp.status_code == 200
    tokens = resp.json()

    for record in caplog.records:
        message = record.getMessage()
        assert tokens["access_token"] not in message
        assert tokens["refresh_token"] not in message
        assert "authorization" not in message.lower()
