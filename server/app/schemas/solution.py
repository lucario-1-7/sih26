import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SolutionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    project_id: uuid.UUID
    title: str = Field(..., min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=5000)


class SolutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: str | None
    created_at: datetime
    updated_at: datetime
