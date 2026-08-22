import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import MilestoneStatus


class MilestoneCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(..., min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    due_date: date | None = None
    order: int = Field(default=0, ge=0)


class MilestoneUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    due_date: date | None = None
    order: int | None = Field(default=None, ge=0)
    status: MilestoneStatus | None = None


class MilestoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: str | None
    due_date: date | None
    status: MilestoneStatus
    completed_at: datetime | None
    order: int
    created_at: datetime
    updated_at: datetime
