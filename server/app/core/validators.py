"""Shared field-level validators for Pydantic request schemas.

Single source of truth for the Indian mobile number format: everywhere a
phone number is accepted from a client (OTP request/verify, superadmin user
provisioning) must reject the same malformed input, before it ever reaches a
repository lookup or an OTP provider.
"""

import re

INDIAN_PHONE_RE = re.compile(r"^\+91[6-9]\d{9}$")


def validate_indian_phone(value: str) -> str:
    """+91 followed by a 10-digit Indian mobile number starting 6-9. Rejects
    missing/duplicated country codes, wrong lengths, and non-digit
    characters. Whitespace is not stripped here: schemas using this already
    set `str_strip_whitespace=True`, so surrounding whitespace never reaches
    this validator."""
    if not INDIAN_PHONE_RE.fullmatch(value):
        raise ValueError("Phone number must be a valid +91XXXXXXXXXX Indian mobile number")
    return value
