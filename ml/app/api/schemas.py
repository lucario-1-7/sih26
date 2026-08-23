from pydantic import BaseModel, ConfigDict, Field


class EmbedRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(..., min_length=1, max_length=10000)


class EmbedResponse(BaseModel):
    embedding: list[float]
    model_name: str
    dimension: int


class DuplicateCandidateIn(BaseModel):
    id: str
    embedding: list[float]


class DuplicateCandidatesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query_embedding: list[float]
    candidates: list[DuplicateCandidateIn]
    threshold: float | None = None


class DuplicateCandidateOut(BaseModel):
    id: str
    similarity_score: float
    is_candidate: bool
    model_name: str
    model_version: str


class DuplicateCandidatesResponse(BaseModel):
    ranked_candidates: list[DuplicateCandidateOut]


class MatchCandidateIn(BaseModel):
    id: str
    embedding: list[float]
    domain_tags: list[str] = Field(default_factory=list)
    type: str | None = None


class MatchRankRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query_embedding: list[float]
    query_domain_tags: list[str] = Field(default_factory=list)
    candidates: list[MatchCandidateIn]


class RankedMatchOut(BaseModel):
    id: str
    score: float
    breakdown: dict[str, float]
    rationale: str
    type: str | None = None


class MatchRankResponse(BaseModel):
    ranked_matches: list[RankedMatchOut]


class ConsortiumRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ranked_matches: list[RankedMatchOut]
    team_size: int = Field(default=3, ge=1, le=10)


class ConsortiumMemberOut(BaseModel):
    organization_id: str
    role: str
    score: float
    rationale: str


class ConsortiumResponse(BaseModel):
    members: list[ConsortiumMemberOut]


class ScoreRequestFieldIntensity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    frequency: float = Field(..., ge=0, le=1)
    severity: float = Field(..., ge=0, le=1)
    recency_days: float = Field(..., ge=0)
    geographic_spread: float = Field(..., ge=0, le=1)


class ScoreRequestPriority(BaseModel):
    model_config = ConfigDict(extra="forbid")
    field_intensity: float = Field(..., ge=0, le=1)
    community_impact: float = Field(..., ge=0, le=1)
    cluster_size: int = Field(..., ge=0)


class ScoreRequestTractability(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resource_availability: float = Field(..., ge=0, le=1)
    historical_resolution_rate: float = Field(..., ge=0, le=1)
    complexity: float = Field(..., ge=0, le=1)


class ScoreResponse(BaseModel):
    score: float
    breakdown: dict[str, float]
    rationale: str
    weight_version: str


class DomainClassifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    embedding: list[float] = Field(..., min_length=1)


class DomainAlternativeOut(BaseModel):
    domain: str
    confidence: float


class DomainClassifyResponse(BaseModel):
    domain: str
    confidence: float
    alternatives: list[DomainAlternativeOut]
    needs_review: bool
    source: str
    model_version: str


class FieldClassifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(..., min_length=1, max_length=10000)
    domain: str = Field(..., min_length=1, max_length=50)
    embedding: list[float] = Field(..., min_length=1)


class FieldClassifyResponse(BaseModel):
    field_intensity: float = Field(..., ge=0.0, le=1.0)
    label: str
    needs_review: bool
    source: str
    model_version: str
