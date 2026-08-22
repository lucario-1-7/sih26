import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectParticipantCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(..., min_length=2, max_length=200)
    department: str | None = Field(default=None, max_length=200)
    academic_year: str | None = Field(default=None, max_length=20)
    registration_id: str | None = Field(default=None, max_length=100)
    participation_role: str = Field(default="member", max_length=100)


class ProjectParticipantUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str | None = Field(default=None, min_length=2, max_length=200)
    department: str | None = Field(default=None, max_length=200)
    academic_year: str | None = Field(default=None, max_length=20)
    registration_id: str | None = Field(default=None, max_length=100)
    participation_role: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None


class ProjectParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    department: str | None
    academic_year: str | None
    registration_id: str | None
    participation_role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
