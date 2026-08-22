import uuid

import pytest

from app.core.security import TokenType, create_token, decode_token, generate_otp, hash_otp, verify_otp_hash


def test_token_round_trip():
    user_id = uuid.uuid4()
    token, jti = create_token(
        user_id=user_id, role="citizen", token_type=TokenType.ACCESS, expires_minutes=15
    )
    payload = decode_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "citizen"
    assert payload["type"] == "access"
    assert payload["jti"] == jti


def test_otp_hash_never_stores_plaintext():
    code = generate_otp(6)
    assert len(code) == 6
    assert code.isdigit()
    hashed = hash_otp(code, "+911234567890")
    assert hashed != code
    assert verify_otp_hash(code, "+911234567890", hashed)
    assert not verify_otp_hash("000000", "+911234567890", hashed)
