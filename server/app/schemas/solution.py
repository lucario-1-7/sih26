import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import SolutionStatus


class SolutionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    project_id: uuid.UUID
    title: str = Field(..., min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    outcome: str | None = Field(default=None, max_length=5000)


class SolutionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    outcome: str | None = Field(default=None, max_length=5000)
    status: SolutionStatus | None = None


class SolutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: str | None
    outcome: str | None
    status: SolutionStatus
    created_at: datetime
    updated_at: datetime


class ReplicationCandidateResponse(BaseModel):
    cluster_id: uuid.UUID
    cluster_title: str
    similarity: float
