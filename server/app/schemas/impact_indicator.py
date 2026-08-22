import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ImpactIndicatorCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(..., min_length=3, max_length=200)
    unit: str = Field(..., min_length=1, max_length=50)
    baseline_value: float | None = None
    baseline_date: date | None = None
    target_value: float | None = None


class ImpactIndicatorEndlineUpdate(BaseModel):
    """Faculty-submitted, unverified claim of the endline outcome."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    actual_value: float = Field(...)
    endline_date: date
    endline_evidence: str | None = Field(default=None, max_length=5000)


class ImpactIndicatorVerify(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approve: bool


class ImpactIndicatorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    unit: str
    baseline_value: float | None
    baseline_date: date | None
    target_value: float | None
    actual_value: float | None
    endline_date: date | None
    endline_evidence: str | None
    verified_at: datetime | None
    verified_by_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
