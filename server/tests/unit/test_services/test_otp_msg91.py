"""Unit tests for the MSG91 OTP Widget provider. Every network call is
mocked via httpx.MockTransport — the real MSG91 API is never called from
this file. See scripts/msg91_smoke_test.py for the manual, credentials-
required smoke test against the real provider.
"""

import httpx
import pytest

from app.core.config import get_settings
from app.services import otp_msg91
from app.services.otp_sender import OtpDeliveryError


def _configure_msg91(monkeypatch, widget_id="test-widget", token_auth="test-token"):
    monkeypatch.setenv("MSG91_WIDGET_ID", widget_id)
    monkeypatch.setenv("MSG91_TOKEN_AUTH", token_auth)
    get_settings.cache_clear()


def _patch_client(monkeypatch, handler):
    monkeypatch.setattr(
        otp_msg91, "_client", lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://mock")
    )


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    yield
    get_settings.cache_clear()


class TestConstruction:
    def test_raises_without_widget_id(self, monkeypatch):
        monkeypatch.setenv("MSG91_WIDGET_ID", "")
        monkeypatch.setenv("MSG91_TOKEN_AUTH", "t")
        get_settings.cache_clear()
        with pytest.raises(OtpDeliveryError):
            otp_msg91.Msg91WidgetOtpProvider()

    def test_raises_without_token_auth(self, monkeypatch):
        monkeypatch.setenv("MSG91_WIDGET_ID", "w")
        monkeypatch.setenv("MSG91_TOKEN_AUTH", "")
        get_settings.cache_clear()
        with pytest.raises(OtpDeliveryError):
            otp_msg91.Msg91WidgetOtpProvider()

    def test_succeeds_when_both_configured(self, monkeypatch):
        _configure_msg91(monkeypatch)
        otp_msg91.Msg91WidgetOtpProvider()  # must not raise


class TestPhoneNormalization:
    def test_strips_leading_plus(self):
        assert otp_msg91.normalize_indian_phone_for_msg91("+919876543210") == "919876543210"

    @pytest.mark.parametrize(
        "bad_phone",
        [
            "9876543210",  # missing +91
            "+91987654321",  # 9 digits
            "+919876543210 ",  # trailing space
            "+1 9876543210",  # wrong country code
            "not-a-phone",
            "",
        ],
    )
    def test_rejects_malformed_numbers(self, bad_phone):
        with pytest.raises(OtpDeliveryError):
            otp_msg91.normalize_indian_phone_for_msg91(bad_phone)


@pytest.mark.asyncio
class TestSend:
    async def test_success_returns_req_id(self, monkeypatch):
        _configure_msg91(monkeypatch)
        captured = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            captured["body"] = request.content.decode()
            return httpx.Response(200, json={"type": "success", "message": "abc123reqid"})

        _patch_client(monkeypatch, handler)
        req_id = await otp_msg91.Msg91WidgetOtpProvider().send("+919876543210")

        assert req_id == "abc123reqid"
        assert "/sendOtpMobile" in captured["url"]
        assert "919876543210" in captured["body"]
        assert "test-token" in captured["body"]

    async def test_send_provider_timeout(self, monkeypatch):
        _configure_msg91(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.TimeoutException("timed out", request=request)

        _patch_client(monkeypatch, handler)
        with pytest.raises(OtpDeliveryError):
            await otp_msg91.Msg91WidgetOtpProvider().send("+919876543210")

    async def test_send_provider_connection_error(self, monkeypatch):
        _configure_msg91(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("refused", request=request)

        _patch_client(monkeypatch, handler)
        with pytest.raises(OtpDeliveryError):
            await otp_msg91.Msg91WidgetOtpProvider().send("+919876543210")

    async def test_send_provider_401_never_leaks_the_token(self, monkeypatch):
        _configure_msg91(monkeypatch, token_auth="super-secret-widget-token")

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(401, json={"type": "error", "message": "invalid tokenAuth"})

        _patch_client(monkeypatch, handler)
        with pytest.raises(OtpDeliveryError) as exc_info:
            await otp_msg91.Msg91WidgetOtpProvider().send("+919876543210")
        assert "super-secret-widget-token" not in str(exc_info.value)

    async def test_send_provider_4xx(self, monkeypatch):
        _configure_msg91(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(422, json={"type": "error", "message": "invalid widgetId"})

        _patch_client(monkeypatch, handler)
        with pytest.raises(OtpDeliveryError):
            await otp_msg91.Msg91WidgetOtpProvider().send("+919876543210")

    async def test_send_provider_5xx(self, monkeypatch):
        _configure_msg91(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(503, text="upstream unavailable")

        _patch_client(monkeypatch, handler)
        with pytest.raises(OtpDeliveryError):
            await otp_msg91.Msg91WidgetOtpProvider().send("+919876543210")

    async def test_send_malformed_json_response(self, monkeypatch):
        _configure_msg91(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=b"{not valid json", headers={"content-type": "application/json"})

        _patch_client(monkeypatch, handler)
        with pytest.raises(OtpDeliveryError):
            await otp_msg91.Msg91WidgetOtpProvider().send("+919876543210")

    async def test_send_200_with_type_error_body_is_a_delivery_failure(self, monkeypatch):
        """MSG91 can return HTTP 200 with a JSON error body (e.g. rejected
        widget config) — this must not be treated as a successful send."""
        _configure_msg91(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"type": "error", "message": "widget misconfigured"})

        _patch_client(monkeypatch, handler)
        with pytest.raises(OtpDeliveryError):
            await otp_msg91.Msg91WidgetOtpProvider().send("+919876543210")

    async def test_send_success_with_empty_req_id_is_a_delivery_failure(self, monkeypatch):
        _configure_msg91(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"type": "success", "message": ""})

        _patch_client(monkeypatch, handler)
        with pytest.raises(OtpDeliveryError):
            await otp_msg91.Msg91WidgetOtpProvider().send("+919876543210")

    async def test_malformed_phone_never_reaches_the_network(self, monkeypatch):
        _configure_msg91(monkeypatch)
        called = False

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal called
            called = True
            return httpx.Response(200, json={"type": "success", "message": "x"})

        _patch_client(monkeypatch, handler)
        with pytest.raises(OtpDeliveryError):
            await otp_msg91.Msg91WidgetOtpProvider().send("not-a-real-phone")
        assert called is False


@pytest.mark.asyncio
class TestVerify:
    async def test_verify_success(self, monkeypatch):
        _configure_msg91(monkeypatch)
        captured = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["body"] = request.content.decode()
            return httpx.Response(200, json={"type": "success", "message": "OTP verified"})

        _patch_client(monkeypatch, handler)
        ok = await otp_msg91.Msg91WidgetOtpProvider().verify("+919876543210", "123456", "req-abc")

        assert ok is True
        assert "req-abc" in captured["body"]
        assert "123456" in captured["body"]

    async def test_verify_wrong_code_returns_false_not_an_exception(self, monkeypatch):
        """A rejected OTP is a normal outcome — auth_service must be able to
        treat it exactly like a locally-hashed mismatch (401), not a 503."""
        _configure_msg91(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"type": "error", "message": "OTP not matched"})

        _patch_client(monkeypatch, handler)
        ok = await otp_msg91.Msg91WidgetOtpProvider().verify("+919876543210", "000000", "req-abc")
        assert ok is False

    async def test_verify_provider_timeout_raises_not_false(self, monkeypatch):
        """A provider outage during verify must surface as a 503
        (OtpDeliveryError), never be silently treated as 'wrong code'."""
        _configure_msg91(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.TimeoutException("timed out", request=request)

        _patch_client(monkeypatch, handler)
        with pytest.raises(OtpDeliveryError):
            await otp_msg91.Msg91WidgetOtpProvider().verify("+919876543210", "123456", "req-abc")

    async def test_verify_provider_5xx_raises_not_false(self, monkeypatch):
        _configure_msg91(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(502, text="bad gateway")

        _patch_client(monkeypatch, handler)
        with pytest.raises(OtpDeliveryError):
            await otp_msg91.Msg91WidgetOtpProvider().verify("+919876543210", "123456", "req-abc")

    async def test_verify_malformed_json_raises_not_false(self, monkeypatch):
        _configure_msg91(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=b"not json", headers={"content-type": "application/json"})

        _patch_client(monkeypatch, handler)
        with pytest.raises(OtpDeliveryError):
            await otp_msg91.Msg91WidgetOtpProvider().verify("+919876543210", "123456", "req-abc")


def _configure_auth_key(monkeypatch, auth_key="test-account-key"):
    monkeypatch.setenv("MSG91_AUTH_KEY", auth_key)
    get_settings.cache_clear()


@pytest.mark.asyncio
class TestVerifyWidgetAccessToken:
    """The client-driven flow: the widget already did the real OTP exchange
    directly with MSG91; this only confirms the resulting access-token."""

    async def test_success_message_as_plain_identifier_string(self, monkeypatch):
        _configure_auth_key(monkeypatch)
        captured = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["body"] = request.content.decode()
            return httpx.Response(200, json={"type": "success", "message": "919876543210"})

        _patch_client(monkeypatch, handler)
        phone = await otp_msg91.verify_widget_access_token("real-access-token")

        assert phone == "+919876543210"
        assert "real-access-token" in captured["body"]
        assert "test-account-key" in captured["body"]

    async def test_success_message_as_object_with_mobile_key(self, monkeypatch):
        _configure_auth_key(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"type": "success", "message": {"mobile": "+919876543210"}})

        _patch_client(monkeypatch, handler)
        phone = await otp_msg91.verify_widget_access_token("real-access-token")
        assert phone == "+919876543210"

    async def test_invalid_token_returns_none_not_an_exception(self, monkeypatch):
        """A token MSG91 says is invalid/expired is a normal auth failure —
        auth_service maps it to a 401, never a 503."""
        _configure_auth_key(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"type": "error", "message": "invalid access-token"})

        _patch_client(monkeypatch, handler)
        phone = await otp_msg91.verify_widget_access_token("bad-token")
        assert phone is None

    async def test_missing_or_empty_token_returns_none_never_reaches_the_network(self, monkeypatch):
        _configure_auth_key(monkeypatch)
        called = False

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal called
            called = True
            return httpx.Response(200, json={"type": "success", "message": "919876543210"})

        _patch_client(monkeypatch, handler)
        assert await otp_msg91.verify_widget_access_token("") is None
        assert called is False

    async def test_unparseable_verified_identity_raises_service_error(self, monkeypatch):
        """MSG91 confirmed the token but we can't tell who it is — this is a
        real integration problem (503), not "invalid token" (which would be
        401) and not silently accepted."""
        _configure_auth_key(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"type": "success", "message": {"unexpected_key": "nope"}})

        _patch_client(monkeypatch, handler)
        with pytest.raises(OtpDeliveryError):
            await otp_msg91.verify_widget_access_token("real-access-token")

    async def test_missing_auth_key_raises_service_error(self, monkeypatch):
        monkeypatch.setenv("MSG91_AUTH_KEY", "")
        get_settings.cache_clear()
        with pytest.raises(OtpDeliveryError):
            await otp_msg91.verify_widget_access_token("real-access-token")

    async def test_provider_timeout_raises_not_none(self, monkeypatch):
        """A transport failure must never be silently treated as 'invalid token'."""
        _configure_auth_key(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.TimeoutException("timed out", request=request)

        _patch_client(monkeypatch, handler)
        with pytest.raises(OtpDeliveryError):
            await otp_msg91.verify_widget_access_token("real-access-token")

    async def test_provider_5xx_raises_not_none(self, monkeypatch):
        _configure_auth_key(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(503, text="upstream down")

        _patch_client(monkeypatch, handler)
        with pytest.raises(OtpDeliveryError):
            await otp_msg91.verify_widget_access_token("real-access-token")

    async def test_never_leaks_the_account_auth_key(self, monkeypatch):
        _configure_auth_key(monkeypatch, auth_key="super-secret-account-key")

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(401, json={"type": "error", "message": "invalid authkey"})

        _patch_client(monkeypatch, handler)
        with pytest.raises(OtpDeliveryError) as exc_info:
            await otp_msg91.verify_widget_access_token("real-access-token")
        assert "super-secret-account-key" not in str(exc_info.value)
