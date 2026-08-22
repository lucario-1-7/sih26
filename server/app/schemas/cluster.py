import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ClusterStatus


class ClusterCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(..., min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    theme_id: uuid.UUID | None = None


class ClusterUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    theme_id: uuid.UUID | None = None
    status: ClusterStatus | None = None


class ClusterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    description: str | None
    theme_id: uuid.UUID | None
    status: ClusterStatus
    created_at: datetime
    updated_at: datetime
