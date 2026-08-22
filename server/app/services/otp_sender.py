import logging
from abc import ABC, abstractmethod

from app.core.config import get_settings

logger = logging.getLogger("app.otp")


class OtpSender(ABC):
    @abstractmethod
    async def send(self, phone: str, code: str) -> None: ...


class ConsoleOtpSender(OtpSender):
    """Development-only sender: logs that an OTP was dispatched instead of
    delivering it via SMS.

    No SMS gateway is integrated in this implementation (out of scope per the
    audit — no such provider/credentials exist yet). Swap this for a real
    provider (e.g. MSG91/Twilio) behind the same interface before production
    use.

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


_sender: OtpSender = ConsoleOtpSender()


def get_otp_sender() -> OtpSender:
    return _sender
