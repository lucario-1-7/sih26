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
    # VALIDATOR-only field — see challenge_service.update_challenge for enforcement.
    severity: ChallengeSeverity | None = None


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
    created_at: datetime
    updated_at: datetime
