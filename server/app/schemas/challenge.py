import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ChallengeStatus


class ChallengeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=5000)
    administrative_area_id: uuid.UUID
    pin_code: str | None = Field(default=None, min_length=6, max_length=6)


class ChallengeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str | None = Field(default=None, min_length=5, max_length=200)
    description: str | None = Field(default=None, min_length=20, max_length=5000)


class ChallengeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    description: str
    status: ChallengeStatus
    submitted_by_id: uuid.UUID
    administrative_area_id: uuid.UUID
    pin_code: str | None
    cluster_id: uuid.UUID | None
    duplicate_of_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
