import logging
from abc import ABC, abstractmethod

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
    use. The code is deliberately never logged or returned in any API
    response — "No plaintext OTPs" is a hard rule (CLAUDE.md), including in
    development. Tests that need the code inject a fake OtpSender instead
    (see tests/integration/test_api/test_auth_flow.py).
    """

    async def send(self, phone: str, code: str) -> None:
        logger.info("otp_dispatched", extra={"phone": phone})


_sender: OtpSender = ConsoleOtpSender()


def get_otp_sender() -> OtpSender:
    return _sender
