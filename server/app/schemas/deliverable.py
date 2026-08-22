import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DeliverableStatus


class DeliverableCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(..., min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    due_date: date | None = None


class DeliverableUpdate(BaseModel):
    """Faculty submits evidence (status -> SUBMITTED); verification is a
    separate action restricted to Coordinator/Superadmin — see
    deliverable_service.verify_deliverable."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    due_date: date | None = None
    evidence: str | None = Field(default=None, max_length=5000)


class DeliverableVerify(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approve: bool


class DeliverableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: str | None
    due_date: date | None
    status: DeliverableStatus
    evidence: str | None
    submitted_at: datetime | None
    verified_at: datetime | None
    verified_by_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
