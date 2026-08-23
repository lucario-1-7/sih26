from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.validators import validate_indian_phone


class OtpRequestIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    phone: str = Field(..., min_length=8, max_length=20)

    _validate_phone = field_validator("phone")(validate_indian_phone)


class OtpVerifyIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    phone: str = Field(..., min_length=8, max_length=20)
    code: str = Field(..., min_length=4, max_length=8)

    _validate_phone = field_validator("phone")(validate_indian_phone)


class RefreshIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh_token: str


class DemoLoginIn(BaseModel):
    """PRESENTATION-ONLY. See app.services.auth_service.DEMO_PERSONAS —
    rejected entirely unless Settings.DEMO_MODE is explicitly on."""

    model_config = ConfigDict(extra="forbid")
    persona: str = Field(..., min_length=1, max_length=64)


class Msg91WidgetVerifyIn(BaseModel):
    """The client-side MSG91 OTP Widget already completed the real OTP
    exchange with MSG91 directly; this is only the access-token it returned
    on success. The backend never receives (and never trusts) a client-
    supplied phone number for this flow — see auth_service.verify_msg91_widget_token."""

    model_config = ConfigDict(extra="forbid")
    access_token: str = Field(..., min_length=1)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
