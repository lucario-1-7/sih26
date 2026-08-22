"""Development-only OTP retrieval.

No SMS gateway is integrated (see `otp_sender.ConsoleOtpSender`), which
makes local development painful without some way to retrieve the code a
developer just requested. This module exists solely for that — it is never
active outside `ENVIRONMENT=development`.

Design:
- In-process memory only. Nothing here is ever persisted to the database,
  written to a log record, or returned by any production API response.
- Every entry point re-checks `settings.ENVIRONMENT` itself (not just the
  route that calls it), so even a misrouted call or a future refactor that
  forgets to gate the endpoint still can't leak or store a code outside dev.
- `get_settings()` is cached per-process (`@lru_cache`), so this correctly
  reflects `ENVIRONMENT` at process start — consistent with how the rest of
  the app treats settings.
"""
from __future__ import annotations

import threading

from app.core.config import get_settings

_lock = threading.Lock()
_latest_by_phone: dict[str, str] = {}


def _dev_mode_enabled() -> bool:
    return get_settings().ENVIRONMENT == "development"


def store_dev_otp(phone: str, code: str) -> None:
    """No-op outside development — never stores a code in any other environment."""
    if not _dev_mode_enabled():
        return
    with _lock:
        _latest_by_phone[phone] = code


def get_dev_otp(phone: str) -> str | None:
    """Returns None outside development, or if no OTP is on record for `phone`."""
    if not _dev_mode_enabled():
        return None
    with _lock:
        return _latest_by_phone.get(phone)
