import logging
from abc import ABC, abstractmethod

from app.core.config import get_settings

logger = logging.getLogger("app.otp")


class OtpDeliveryError(Exception):
    """Raised by any sender/provider implementation when it cannot deliver or
    verify the OTP — provider outage, rejected credentials, malformed
    response, missing production configuration, etc. Mapped to a 503 by the
    global exception handler (see app.core.errors) — the auth service and
    callers never need to know which sender is active or why delivery
    failed; they only ever see this one type. Never carries a provider auth
    key/token, raw response body, or stack trace in its message."""


class OtpSender(ABC):
    """Delivery-only: WE generate the code, hash it, store it, and check it
    on verify (app.core.security.generate_otp / hash_otp / verify_otp_hash).
    This kind of sender only has to get that code to the user. The
    console/dev sender is this kind."""

    @abstractmethod
    async def send(self, phone: str, code: str) -> None: ...


class NativeOtpProvider(ABC):
    """Provider-native: the PROVIDER generates and verifies the code — we
    never see or hash it ourselves. MSG91's OTP Widget is this kind. Selected
    behind the exact same `get_otp_sender()` seam as OtpSender; auth_service
    branches on `isinstance` and otherwise treats both kinds identically for
    everything else (expiry, max-attempts, resend cooldown, audit logging,
    JWT issuance) — see app/services/auth_service.py."""

    @abstractmethod
    async def send(self, phone: str) -> str:
        """Returns the provider's own request reference (e.g. MSG91 Widget's
        `reqId`), which must be persisted and presented back on verify."""

    @abstractmethod
    async def verify(self, phone: str, code: str, provider_ref: str) -> bool:
        """True if the provider confirms `code` is correct for `provider_ref`."""


class ConsoleOtpSender(OtpSender):
    """Development-only sender: logs that an OTP was dispatched instead of
    delivering it via SMS.

    "No plaintext OTPs" (CLAUDE.md) is a hard rule for production. The one
    narrow, explicitly-requested exception: when `ENVIRONMENT=="development"`
    (checked fresh on every call — never cached across a hypothetical
    environment change), the code is logged so a developer can read it
    straight from `docker compose logs -f server` without a second HTTP
    round-trip to the dev OTP-retrieval endpoint. Outside development this
    branch never executes — see test_dev_otp.py for proof the plaintext
    string never reaches the log stream when ENVIRONMENT != "development".
    Note: log `extra=` fields are dropped by the current formatter (see
    core/logging.py) — the phone/code must be interpolated into the message
    itself to actually appear in output.
    """

    async def send(self, phone: str, code: str) -> None:
        if get_settings().ENVIRONMENT == "development":
            logger.info(
                "otp_dispatched_dev_only phone=%s otp=%s (local development only — never logged in production)",
                phone,
                code,
            )
            return
        logger.info("otp_dispatched", extra={"phone": phone})


_sender: OtpSender | NativeOtpProvider | None = None


def _build_sender() -> OtpSender | NativeOtpProvider:
    """Selects the sender by ENVIRONMENT, never by which env vars happen to be
    set — so a stray MSG91 credential left in a dev .env can never silently
    start sending real SMS locally, and a missing one in production can
    never silently fall back to logging plaintext OTPs.

    - production: MSG91 always. If MSG91_WIDGET_ID/MSG91_TOKEN_AUTH are
      missing, construction raises OtpDeliveryError — every OTP request then
      fails safely with a 503 (never a crash of the whole app at startup,
      never a silent console fallback) until an operator fixes the config.
    - anything else (development, test, ...): MSG91 if fully configured
      (lets a developer point a local run at real MSG91 to test physical SMS
      delivery), otherwise the console/dev-store sender.
    """
    settings = get_settings()
    if settings.ENVIRONMENT == "production":
        from app.services.otp_msg91 import Msg91WidgetOtpProvider

        return Msg91WidgetOtpProvider()

    if settings.MSG91_WIDGET_ID and settings.MSG91_TOKEN_AUTH:
        from app.services.otp_msg91 import Msg91WidgetOtpProvider

        return Msg91WidgetOtpProvider()

    return ConsoleOtpSender()


def get_otp_sender() -> OtpSender | NativeOtpProvider:
    global _sender
    if _sender is None:
        _sender = _build_sender()
    return _sender
