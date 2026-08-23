import pytest

from app.core.config import get_settings
from app.services import otp_sender
from app.services.otp_msg91 import Msg91WidgetOtpProvider
from app.services.otp_sender import ConsoleOtpSender, OtpDeliveryError, get_otp_sender


@pytest.fixture(autouse=True)
def _reset_sender_singleton():
    otp_sender._sender = None
    yield
    otp_sender._sender = None
    get_settings.cache_clear()


def test_development_without_msg91_config_uses_console_sender(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("MSG91_WIDGET_ID", "")
    monkeypatch.setenv("MSG91_TOKEN_AUTH", "")
    get_settings.cache_clear()

    assert isinstance(get_otp_sender(), ConsoleOtpSender)


def test_development_with_msg91_config_uses_msg91_provider(monkeypatch):
    """A developer can point local dev at real MSG91 to test physical SMS
    delivery, without ENVIRONMENT ever having to say "production"."""
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("MSG91_WIDGET_ID", "w")
    monkeypatch.setenv("MSG91_TOKEN_AUTH", "t")
    get_settings.cache_clear()

    assert isinstance(get_otp_sender(), Msg91WidgetOtpProvider)


def test_production_without_msg91_config_fails_safely_not_a_console_fallback(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("MSG91_WIDGET_ID", "")
    monkeypatch.setenv("MSG91_TOKEN_AUTH", "")
    get_settings.cache_clear()

    with pytest.raises(OtpDeliveryError):
        get_otp_sender()


def test_production_with_msg91_config_uses_msg91_provider(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("MSG91_WIDGET_ID", "w")
    monkeypatch.setenv("MSG91_TOKEN_AUTH", "t")
    get_settings.cache_clear()

    assert isinstance(get_otp_sender(), Msg91WidgetOtpProvider)


def test_a_stray_widget_id_alone_without_token_auth_still_falls_back_to_console_in_dev(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("MSG91_WIDGET_ID", "w")
    monkeypatch.setenv("MSG91_TOKEN_AUTH", "")
    get_settings.cache_clear()

    assert isinstance(get_otp_sender(), ConsoleOtpSender)


def test_sender_is_cached_after_first_successful_build(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("MSG91_WIDGET_ID", "")
    monkeypatch.setenv("MSG91_TOKEN_AUTH", "")
    get_settings.cache_clear()

    first = get_otp_sender()
    second = get_otp_sender()
    assert first is second
