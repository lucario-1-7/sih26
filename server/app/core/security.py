import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from enum import StrEnum

import jwt

from app.core.config import get_settings


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_token(
    *, user_id: uuid.UUID, role: str, token_type: TokenType, expires_minutes: int
) -> tuple[str, str]:
    """Returns (token, jti)."""
    settings = get_settings()
    jti = str(uuid.uuid4())
    now = _now()
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": token_type.value,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
        "jti": jti,
    }
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        headers={"kid": settings.JWT_KEY_ID},
    )
    return token, jti


def decode_token(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def generate_otp(length: int) -> str:
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def hash_otp(code: str, phone: str) -> str:
    settings = get_settings()
    return hmac.new(
        settings.SECRET_KEY.encode(), f"{phone}:{code}".encode(), hashlib.sha256
    ).hexdigest()


def verify_otp_hash(code: str, phone: str, expected_hash: str) -> bool:
    return hmac.compare_digest(hash_otp(code, phone), expected_hash)
