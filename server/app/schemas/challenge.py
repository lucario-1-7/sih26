import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ChallengeSeverity, ChallengeStatus


class ChallengeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=5000)
    administrative_area_id: uuid.UUID
    pin_code: str | None = Field(default=None, min_length=6, max_length=6)
    # Only meaningful (and only accepted) when the submitter is a
    # FIELD_ASSISTANT — the citizen being reported for has no account.
    # Silently ignored for CITIZEN submitters; see challenge_service.create_challenge.
    on_behalf_of_name: str | None = Field(default=None, min_length=2, max_length=200)
    on_behalf_of_phone: str | None = Field(default=None, min_length=8, max_length=20)


class ChallengeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str | None = Field(default=None, min_length=5, max_length=200)
    description: str | None = Field(default=None, min_length=20, max_length=5000)
    # VALIDATOR/SUPERADMIN-only fields — see challenge_service.update_challenge
    # for enforcement and existence checks.
    severity: ChallengeSeverity | None = None
    cluster_id: uuid.UUID | None = None


class ChallengeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    description: str
    status: ChallengeStatus
    severity: ChallengeSeverity | None
    submitted_by_id: uuid.UUID
    administrative_area_id: uuid.UUID
    pin_code: str | None
    cluster_id: uuid.UUID | None
    duplicate_of_id: uuid.UUID | None
    on_behalf_of_name: str | None
    on_behalf_of_phone: str | None
    # AI-suggested, advisory only — never authoritative. Null until the
    # duplicate-candidates job classifies the challenge.
    content_domain: str | None
    content_domain_confidence: float | None
    content_domain_needs_review: bool | None
    content_domain_source: str | None
    content_field_intensity: float | None
    content_field_label: str | None
    content_field_needs_review: bool | None
    content_field_source: str | None
    created_at: datetime
    updated_at: datetime
