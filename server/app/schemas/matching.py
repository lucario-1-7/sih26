import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ConsortiumStatus, OrganizationType


class OrganizationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(..., min_length=2, max_length=200)
    type: OrganizationType
    domain_tags: list[str] = Field(default_factory=list, max_length=20)
    description: str | None = Field(default=None, max_length=5000)


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    type: OrganizationType
    domain_tags: list[str]
    description: str | None
    created_at: datetime


class MatchResult(BaseModel):
    organization_id: uuid.UUID
    score: float
    breakdown: dict[str, float]
    rationale: str


class ConsortiumMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    organization_id: uuid.UUID
    role: str
    match_score: float | None
    rationale: str | None


class ConsortiumResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID
    status: ConsortiumStatus
    created_at: datetime


class ConsortiumRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    team_size: int = Field(default=3, ge=1, le=10)
