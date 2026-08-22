import pytest

from app.services import otp_sender


class CapturingSender(otp_sender.OtpSender):
    def __init__(self):
        self.last_code: str | None = None

    async def send(self, phone: str, code: str) -> None:
        self.last_code = code


@pytest.mark.asyncio
async def test_otp_login_round_trip(client, monkeypatch):
    sender = CapturingSender()
    monkeypatch.setattr(otp_sender, "_sender", sender)
    monkeypatch.setattr(otp_sender, "get_otp_sender", lambda: sender)
    import app.services.auth_service as auth_service

    monkeypatch.setattr(auth_service, "get_otp_sender", lambda: sender)

    phone = "+919876500001"
    resp = await client.post("/api/v1/auth/otp/request", json={"phone": phone})
    assert resp.status_code == 202
    assert sender.last_code is not None

    resp = await client.post("/api/v1/auth/otp/verify", json={"phone": phone, "code": sender.last_code})
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens and "refresh_token" in tokens

    resp = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert resp.status_code == 200
    assert resp.json()["phone"] == phone

    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    assert resp.json()["access_token"] != tokens["access_token"]


@pytest.mark.asyncio
async def test_otp_verify_with_wrong_code_is_rejected(client, monkeypatch):
    sender = CapturingSender()
    import app.services.auth_service as auth_service

    monkeypatch.setattr(auth_service, "get_otp_sender", lambda: sender)

    phone = "+919876500002"
    await client.post("/api/v1/auth/otp/request", json={"phone": phone})

    resp = await client.post("/api/v1/auth/otp/verify", json={"phone": phone, "code": "000000"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_requires_auth(client):
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_verifying_with_the_most_recently_requested_otp_succeeds(client, monkeypatch):
    """Regression test for the otp_codes.created_at frozen-default bug (see
    migration d4e5f6a7b8c9): every row's created_at used to be pinned to the
    moment the table was created, so OtpRepository.get_latest_active()'s
    `ORDER BY created_at DESC` could return an arbitrary older OTP instead of
    the one just issued — a genuinely correct, freshly-requested code would
    then fail verification. Requesting twice and verifying with the second
    (truly latest) code must succeed."""
    codes: list[str] = []

    class RecordingSender(otp_sender.OtpSender):
        async def send(self, phone: str, code: str) -> None:
            codes.append(code)

    sender = RecordingSender()
    import app.services.auth_service as auth_service

    monkeypatch.setattr(auth_service, "get_otp_sender", lambda: sender)

    phone = "+919876500099"
    resp = await client.post("/api/v1/auth/otp/request", json={"phone": phone})
    assert resp.status_code == 202
    resp = await client.post("/api/v1/auth/otp/request", json={"phone": phone})
    assert resp.status_code == 202
    assert len(codes) == 2
    latest_code = codes[-1]

    resp = await client.post("/api/v1/auth/otp/verify", json={"phone": phone, "code": latest_code})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
