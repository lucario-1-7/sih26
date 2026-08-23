import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.validators import validate_indian_phone
from app.models.enums import Domain, Role


class UserCreate(BaseModel):
    """Superadmin-only: provisions a login for a GOVERNMENT/UNIVERSITY/
    INDUSTRY/SUPERADMIN staff member. CITIZEN accounts self-provision via the
    OTP flow instead (see auth_service.request_otp)."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    phone: str = Field(..., min_length=8, max_length=20)
    name: str = Field(..., min_length=2, max_length=200)
    role: Role
    domain: Domain
    organization_id: uuid.UUID | None = None
    administrative_area_id: uuid.UUID | None = None

    _validate_phone = field_validator("phone")(validate_indian_phone)


class UserUpdate(BaseModel):
    """Superadmin-only: role/domain/organization/active-status management."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str | None = Field(default=None, min_length=2, max_length=200)
    role: Role | None = None
    domain: Domain | None = None
    organization_id: uuid.UUID | None = None
    administrative_area_id: uuid.UUID | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    phone: str
    name: str
    role: Role
    domain: Domain
    organization_id: uuid.UUID | None
    administrative_area_id: uuid.UUID | None
    is_active: bool
    created_at: datetime
