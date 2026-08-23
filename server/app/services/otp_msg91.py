"""Production OTP provider: MSG91's OTP Widget (native generate + verify).

MSG91 offers two integration modes:
  (a) Widget-native: MSG91 generates AND verifies the OTP itself.
  (b) Delivery-only: we generate/hash/verify locally, MSG91 only sends the SMS.

This project uses (a) — a deliberate choice, made explicitly because the
account this ships against is already provisioned as an MSG91 OTP Widget
(WIDGET_ID + widget-specific TOKEN_AUTH), not a DLT SMS template. See
app/services/otp_sender.py:NativeOtpProvider for how this plugs into
auth_service without disturbing anything else about the login flow —
expiry, max-attempts, resend cooldown, audit logging, and JWT issuance are
all identical regardless of which provider generated the code.

Endpoint contract below is taken directly from MSG91's own official Kotlin
SDK source (Walkover-Web-Solution/sendotp-kotlin-sdk, ApiUrls.kt /
OTPWidget.kt) — not guessed:

    POST https://control.msg91.com/api/v5/widget/sendOtpMobile
      body: {"widgetId": ..., "tokenAuth": ..., "identifier": "91XXXXXXXXXX"}
      success: {"type": "success", "message": "<reqId>"}
      failure: {"type": "error", "message": "<reason>"}

    POST https://control.msg91.com/api/v5/widget/verifyOtp
      body: {"widgetId": ..., "tokenAuth": ..., "otp": "123456", "reqId": "<reqId>"}
      success: {"type": "success", "message": "..."}
      failure: {"type": "error", "message": "<reason>"}

TOKEN_AUTH is the WIDGET's own token (from the widget's "Server-Side
Integration" panel in the MSG91 dashboard) — it is not the account-level
Auth Key, and authentication here is entirely via the JSON body, not a
header. Getting this value from the wrong place in the dashboard is the most
likely real-world setup mistake — see .env.example.

Indian DLT requirement: the widget's underlying SMS template still needs
DLT registration/approval on the MSG91 dashboard before it will actually
deliver to Indian numbers, even though this code never touches template_id
directly — that's configured once, in the widget's own settings.
"""

from __future__ import annotations

import logging
import re

import httpx

from app.core.config import get_settings
from app.core.validators import INDIAN_PHONE_RE
from app.services.otp_sender import NativeOtpProvider, OtpDeliveryError

logger = logging.getLogger("app.otp.msg91")


def normalize_indian_phone_for_msg91(phone: str) -> str:
    """The app stores/issues phones as +91XXXXXXXXXX everywhere (JWT `sub`
    lookups, audit logs). MSG91's `identifier` parameter wants the country
    code without the leading '+' (e.g. "919876543210"). Rejects anything
    that isn't exactly a +91 Indian mobile number rather than guessing at a
    malformed one."""
    if not INDIAN_PHONE_RE.fullmatch(phone):
        raise OtpDeliveryError("Phone number is not a valid +91XXXXXXXXXX Indian mobile number")
    return phone[1:]  # "+919876543210" -> "919876543210"


def _client() -> httpx.AsyncClient:
    """Factory seam so tests can monkeypatch this one function instead of the
    global httpx.AsyncClient — same pattern as app.services.ml_client._client."""
    settings = get_settings()
    return httpx.AsyncClient(base_url=settings.MSG91_BASE_URL, timeout=settings.MSG91_TIMEOUT_SECONDS)


async def _post(path: str, body: dict, *, phone_suffix: str) -> dict:
    """Shared TRANSPORT-level handling for both sendOtpMobile and verifyOtp —
    timeouts, connection failures, HTTP-level rejections, and malformed
    bodies are all genuine provider/config failures (-> OtpDeliveryError,
    503) regardless of which call is being made.

    Deliberately does NOT interpret the parsed `{"type": ...}` field — a
    well-formed "type": "error" response means different things for the two
    callers (send: delivery genuinely failed; verify: the code was simply
    wrong, a normal 401 outcome, not a 503) — see send()/verify() below.
    """
    try:
        async with _client() as client:
            response = await client.post(path, json=body)
    except httpx.TimeoutException as exc:
        logger.error("msg91_timeout path=%s phone_suffix=%s", path, phone_suffix)
        raise OtpDeliveryError("MSG91 request timed out") from exc
    except httpx.HTTPError as exc:
        logger.error("msg91_network_error path=%s phone_suffix=%s error=%s", path, phone_suffix, type(exc).__name__)
        raise OtpDeliveryError("MSG91 request failed") from exc

    if response.status_code == 401:
        logger.error("msg91_unauthorized path=%s phone_suffix=%s", path, phone_suffix)
        raise OtpDeliveryError("MSG91 rejected the configured widget credentials")
    if response.status_code >= 500:
        logger.error("msg91_server_error path=%s status=%s phone_suffix=%s", path, response.status_code, phone_suffix)
        raise OtpDeliveryError(f"MSG91 server error ({response.status_code})")
    if response.status_code >= 400:
        logger.error("msg91_client_error path=%s status=%s phone_suffix=%s", path, response.status_code, phone_suffix)
        raise OtpDeliveryError(f"MSG91 rejected the request ({response.status_code})")

    try:
        parsed = response.json()
    except ValueError as exc:
        logger.error("msg91_malformed_response path=%s phone_suffix=%s", path, phone_suffix)
        raise OtpDeliveryError("MSG91 returned a malformed response") from exc

    if not isinstance(parsed, dict) or "type" not in parsed:
        logger.error("msg91_unexpected_response_shape path=%s phone_suffix=%s", path, phone_suffix)
        raise OtpDeliveryError("MSG91 returned an unexpected response shape")

    return parsed


class Msg91WidgetOtpProvider(NativeOtpProvider):
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.MSG91_WIDGET_ID or not settings.MSG91_TOKEN_AUTH:
            raise OtpDeliveryError(
                "MSG91_WIDGET_ID and MSG91_TOKEN_AUTH must both be set to use the MSG91 OTP Widget provider"
            )

    async def send(self, phone: str) -> str:
        settings = get_settings()
        identifier = normalize_indian_phone_for_msg91(phone)
        phone_suffix = phone[-4:]  # safe to log — never enough to identify or replay

        body = {
            "widgetId": settings.MSG91_WIDGET_ID,
            "tokenAuth": settings.MSG91_TOKEN_AUTH,
            "identifier": identifier,
        }
        parsed = await _post("/sendOtpMobile", body, phone_suffix=phone_suffix)
        if parsed.get("type") != "success":
            # Here, "type": "error" IS a genuine delivery failure — no OTP
            # was generated or sent, so this must surface as a 503, exactly
            # like a transport-level failure.
            message = str(parsed.get("message", ""))[:200]
            logger.error("msg91_send_rejected phone_suffix=%s message=%s", phone_suffix, message)
            raise OtpDeliveryError("MSG91 rejected OTP delivery")

        req_id = str(parsed.get("message", ""))
        if not req_id:
            logger.error("msg91_send_missing_req_id phone_suffix=%s", phone_suffix)
            raise OtpDeliveryError("MSG91 did not return a request reference")

        logger.info("msg91_otp_dispatched phone_suffix=%s", phone_suffix)
        return req_id

    async def verify(self, phone: str, code: str, provider_ref: str) -> bool:
        settings = get_settings()
        phone_suffix = phone[-4:]

        body = {
            "widgetId": settings.MSG91_WIDGET_ID,
            "tokenAuth": settings.MSG91_TOKEN_AUTH,
            "otp": code,
            "reqId": provider_ref,
        }
        parsed = await _post("/verifyOtp", body, phone_suffix=phone_suffix)
        if parsed.get("type") != "success":
            # Here, "type": "error" means "the code was wrong" (or the reqId
            # expired) — a normal, expected verification outcome, not a
            # provider failure. auth_service treats a `False` return exactly
            # like a locally-hashed wrong code (bumps attempt_count, returns
            # a 401), never a 503.
            message = str(parsed.get("message", ""))[:200]
            logger.info("msg91_otp_verification_failed phone_suffix=%s message=%s", phone_suffix, message)
            return False
        return True


# ---------------------------------------------------------------------------
# Client-driven widget flow (citizen web + Flutter): the widget runs entirely
# on the client, using WIDGET_ID + TOKEN_AUTH — both meant to be shipped to
# the client per MSG91's own "Client Side Integration" panel, the same way a
# payment provider's publishable key is meant to be public. The client never
# talks to our backend until AFTER the widget already has a verified
# access-token; our job is exactly one call: confirm that token is real.
#
#     POST https://control.msg91.com/api/v5/widget/verifyAccessToken
#       body: {"authkey": <ACCOUNT auth key>, "access-token": "<from widget>"}
#       success: {"type": "success", "message": <verified identity>}
#       failure: {"type": "error", "message": "<reason>"}
#
# MSG91_AUTH_KEY here is the account-level secret and must never reach the
# client — this is the one call in the whole OTP Widget integration that
# uses it, and it is a pure server-to-server call.
#
# MSG91 does not appear to publish a single fixed schema for the "verified
# identity" carried in `message` for this call — it has been observed as
# either the identifier itself or an object containing it. Both are handled
# below; if MSG91 ever returns a third shape, this raises a clear
# OtpDeliveryError (never silently accepts an unverifiable identity) rather
# than guessing.
# ---------------------------------------------------------------------------


def _identifier_to_app_phone(raw: str) -> str | None:
    """MSG91 returns the identifier as digits (e.g. "919876543210"), possibly
    already with a '+'. Converts to this app's canonical +91XXXXXXXXXX.
    Returns None (never guesses) if it isn't unambiguously a 10-digit Indian
    mobile number."""
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("91") and len(digits) == 12:
        national = digits[2:]
    elif len(digits) == 10:
        national = digits
    else:
        return None
    return f"+91{national}"


def _extract_verified_phone(message: object) -> str | None:
    if isinstance(message, str) and message:
        return _identifier_to_app_phone(message)
    if isinstance(message, dict):
        for key in ("mobile", "identifier", "phone", "phone_number"):
            value = message.get(key)
            if isinstance(value, str) and value:
                return _identifier_to_app_phone(value)
    return None


async def verify_widget_access_token(access_token: str) -> str | None:
    """Confirms a widget-issued access-token with MSG91 and returns the
    verified phone in this app's +91XXXXXXXXXX format.

    Returns None — never raises — for a token MSG91 itself says is
    invalid/expired: that is a normal auth failure (the caller maps it to a
    401), not a provider outage. A transport-level failure (timeout,
    network, 5xx, malformed body — anything from `_post`) still raises
    OtpDeliveryError (503), and is never confused with "the token was bad" —
    same "provider-down != wrong-credential" split as verify() above.

    Never trusts a phone number supplied by the client instead of what
    MSG91 verifies — this is the only source of truth for "who did MSG91
    actually confirm owns this phone".
    """
    settings = get_settings()
    if not settings.MSG91_AUTH_KEY:
        raise OtpDeliveryError("MSG91_AUTH_KEY must be configured to verify a widget access token")
    if not access_token or not isinstance(access_token, str):
        return None

    body = {"authkey": settings.MSG91_AUTH_KEY, "access-token": access_token}
    parsed = await _post("/verifyAccessToken", body, phone_suffix="****")

    if parsed.get("type") != "success":
        message = str(parsed.get("message", ""))[:200]
        logger.info("msg91_access_token_verification_failed message=%s", message)
        return None

    phone = _extract_verified_phone(parsed.get("message"))
    if phone is None:
        # MSG91 confirmed the token but returned an identity shape we can't
        # parse — this IS a provider/integration mismatch (503), not a
        # simple invalid token, since we genuinely can't tell who it was.
        logger.error("msg91_access_token_verify_missing_identifier")
        raise OtpDeliveryError("MSG91 did not return a usable verified identifier")

    logger.info("msg91_access_token_verified phone_suffix=%s", phone[-4:])
    return phone
