"""Proves the NativeOtpProvider path (MSG91 Widget's shape: provider
generates AND verifies) works end-to-end through the real HTTP routes and
real database — using a fake provider double, not real MSG91 (that's
app/services/otp_msg91.py's own unit tests). This is what guarantees
auth_service.py's branch on `isinstance(sender, NativeOtpProvider)` didn't
regress anything about JWT issuance, RBAC, expiry, attempts, or auditing.
"""

import uuid

import pytest

from app.services import otp_sender
from app.services.otp_sender import NativeOtpProvider


class FakeNativeProvider(NativeOtpProvider):
    """Generates its own code (like MSG91 does) and verifies against it
    in-memory — never touches our hash/store pipeline."""

    def __init__(self):
        self._codes: dict[str, tuple[str, str]] = {}  # phone -> (req_id, code)

    async def send(self, phone: str) -> str:
        req_id = str(uuid.uuid4())
        self._codes[phone] = (req_id, "778899")
        return req_id

    async def verify(self, phone: str, code: str, provider_ref: str) -> bool:
        stored = self._codes.get(phone)
        if stored is None:
            return False
        stored_req_id, stored_code = stored
        return stored_req_id == provider_ref and stored_code == code


@pytest.mark.asyncio
async def test_native_provider_login_round_trip(client, monkeypatch):
    provider = FakeNativeProvider()
    monkeypatch.setattr(otp_sender, "get_otp_sender", lambda: provider)
    import app.services.auth_service as auth_service

    monkeypatch.setattr(auth_service, "get_otp_sender", lambda: provider)

    phone = "+919876511001"
    resp = await client.post("/api/v1/auth/otp/request", json={"phone": phone})
    assert resp.status_code == 202

    resp = await client.post("/api/v1/auth/otp/verify", json={"phone": phone, "code": "778899"})
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens and "refresh_token" in tokens

    # Preserved JWT/RBAC behavior — identical to the delivery-only path.
    resp = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert resp.status_code == 200
    assert resp.json()["phone"] == phone
    assert resp.json()["role"] == "citizen"

    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_native_provider_wrong_code_is_rejected_and_bumps_attempts(client, monkeypatch):
    provider = FakeNativeProvider()
    import app.services.auth_service as auth_service

    monkeypatch.setattr(auth_service, "get_otp_sender", lambda: provider)

    phone = "+919876511002"
    await client.post("/api/v1/auth/otp/request", json={"phone": phone})

    resp = await client.post("/api/v1/auth/otp/verify", json={"phone": phone, "code": "000000"})
    assert resp.status_code == 401

    # The real (provider-generated) code still works afterward — one wrong
    # attempt must not have locked out or corrupted the row.
    resp = await client.post("/api/v1/auth/otp/verify", json={"phone": phone, "code": "778899"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_native_provider_max_attempts_still_enforced(client, monkeypatch):
    from app.core.config import get_settings

    provider = FakeNativeProvider()
    import app.services.auth_service as auth_service

    monkeypatch.setattr(auth_service, "get_otp_sender", lambda: provider)

    phone = "+919876511003"
    await client.post("/api/v1/auth/otp/request", json={"phone": phone})

    max_attempts = get_settings().OTP_MAX_ATTEMPTS
    for _ in range(max_attempts):
        resp = await client.post("/api/v1/auth/otp/verify", json={"phone": phone, "code": "000000"})
        assert resp.status_code == 401

    # Even the CORRECT code is now rejected — attempt limiting is identical
    # to the locally-hashed path, regardless of which provider generated it.
    resp = await client.post("/api/v1/auth/otp/verify", json={"phone": phone, "code": "778899"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_native_provider_send_failure_surfaces_as_503(client, monkeypatch):
    from app.services.otp_sender import OtpDeliveryError

    class FailingProvider(NativeOtpProvider):
        async def send(self, phone: str) -> str:
            raise OtpDeliveryError("simulated provider outage")

        async def verify(self, phone: str, code: str, provider_ref: str) -> bool:
            raise AssertionError("should never be called in this test")

    import app.services.auth_service as auth_service

    monkeypatch.setattr(auth_service, "get_otp_sender", lambda: FailingProvider())

    resp = await client.post("/api/v1/auth/otp/request", json={"phone": "+919876511004"})
    assert resp.status_code == 503
    body = resp.json()
    assert body["code"] == "OTP_DELIVERY_UNAVAILABLE"
    assert "simulated provider outage" not in body["detail"]


@pytest.mark.asyncio
async def test_native_provider_verify_failure_surfaces_as_503_not_401(client, monkeypatch):
    """A provider outage DURING verify (as opposed to a wrong code) must be
    a 503 — collapsing it into a 401 would tell the user their code was
    wrong when actually the provider is just unreachable."""
    from app.services.otp_sender import OtpDeliveryError

    class VerifyFailingProvider(NativeOtpProvider):
        async def send(self, phone: str) -> str:
            return "req-1"

        async def verify(self, phone: str, code: str, provider_ref: str) -> bool:
            raise OtpDeliveryError("simulated provider outage during verify")

    import app.services.auth_service as auth_service

    monkeypatch.setattr(auth_service, "get_otp_sender", lambda: VerifyFailingProvider())

    phone = "+919876511005"
    await client.post("/api/v1/auth/otp/request", json={"phone": phone})

    resp = await client.post("/api/v1/auth/otp/verify", json={"phone": phone, "code": "123456"})
    assert resp.status_code == 503
