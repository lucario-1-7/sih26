import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import CollaborationStatus, CollaborationType, CommitmentStatus


class CollaborationCreate(BaseModel):
    """Industry-initiated: organization_id is always the acting Industry
    user's own organization — never client-supplied."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    project_id: uuid.UUID
    type: CollaborationType
    proposal: str | None = Field(default=None, max_length=5000)


class CollaborationStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: CollaborationStatus
    proposal: str | None = Field(default=None, max_length=5000)


class CollaborationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    organization_id: uuid.UUID
    project_id: uuid.UUID
    type: CollaborationType
    status: CollaborationStatus
    proposal: str | None
    created_at: datetime
    updated_at: datetime


class CommitmentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    type: CollaborationType
    amount: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    description: str | None = Field(default=None, max_length=2000)


class CommitmentStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: CommitmentStatus
    evidence: str | None = Field(default=None, max_length=2000)


class CommitmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    collaboration_id: uuid.UUID
    type: CollaborationType
    amount: float | None
    currency: str | None
    description: str | None
    status: CommitmentStatus
    evidence: str | None
    created_at: datetime
    updated_at: datetime
