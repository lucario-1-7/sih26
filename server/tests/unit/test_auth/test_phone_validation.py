"""Unit coverage for the shared Indian-mobile-number validator (app.core.
validators.validate_indian_phone), and that it's actually wired into every
request schema that accepts a phone number from a client."""

import pytest
from pydantic import ValidationError

from app.core.validators import validate_indian_phone
from app.schemas.auth import DemoLoginIn, OtpRequestIn, OtpVerifyIn
from app.schemas.user import UserCreate


class TestValidateIndianPhone:
    @pytest.mark.parametrize(
        "phone",
        [
            "+919876543210",
            "+916000000000",
            "+919999999999",
        ],
    )
    def test_accepts_valid_indian_mobile_numbers(self, phone):
        assert validate_indian_phone(phone) == phone

    @pytest.mark.parametrize(
        "phone",
        [
            "9876543210",  # missing +91
            "+91+919876543210",  # doubled +91 prefix
            "+915876543210",  # leading digit 5, not 6-9
            "+919876543",  # too short
            "+9198765432100",  # too long
            "not-a-phone",  # letters
            "+9198765432ab",  # letters mixed in
            "",  # empty
            "+911234567890",  # leading digit 1
        ],
    )
    def test_rejects_malformed_numbers(self, phone):
        with pytest.raises(ValueError):
            validate_indian_phone(phone)


class TestSchemaWiring:
    def test_otp_request_in_rejects_malformed_phone(self):
        with pytest.raises(ValidationError):
            OtpRequestIn(phone="not-a-phone")

    def test_otp_request_in_accepts_valid_phone(self):
        assert OtpRequestIn(phone="+919876543210").phone == "+919876543210"

    def test_otp_verify_in_rejects_malformed_phone(self):
        with pytest.raises(ValidationError):
            OtpVerifyIn(phone="9876543210", code="123456")

    def test_user_create_rejects_malformed_phone(self):
        with pytest.raises(ValidationError):
            UserCreate(phone="+91123", name="Someone", role="citizen", domain="citizen")

    def test_demo_login_in_never_accepts_a_role_field(self):
        # Only `persona` (a string looked up against a fixed server-side
        # allowlist) exists on this schema, a client can never submit a
        # role/domain directly and receive it.
        assert set(DemoLoginIn.model_fields) == {"persona"}
