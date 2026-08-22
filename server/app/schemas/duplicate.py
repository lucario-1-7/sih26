import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DuplicateDecisionType


class DuplicateCandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    challenge_id: uuid.UUID
    candidate_challenge_id: uuid.UUID
    similarity_score: float
    model_name: str
    model_version: str
    created_at: datetime


class DuplicateDecisionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    challenge_id: uuid.UUID
    candidate_challenge_id: uuid.UUID
    decision: DuplicateDecisionType
    reason: str | None = Field(default=None, max_length=2000)


class DuplicateDecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    challenge_id: uuid.UUID
    candidate_challenge_id: uuid.UUID
    decision: DuplicateDecisionType
    reviewer_id: uuid.UUID
    reason: str | None
    created_at: datetime
