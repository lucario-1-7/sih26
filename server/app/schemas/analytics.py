from pydantic import BaseModel


class ChallengeAnalytics(BaseModel):
    total: int
    by_status: dict[str, int]
    by_severity: dict[str, int]
    by_administrative_area: dict[str, int]


class ProjectAnalytics(BaseModel):
    total: int
    by_status: dict[str, int]
    by_organization: dict[str, int]


class IndustryAnalytics(BaseModel):
    organization_count: int
    collaboration_count: int
    collaborations_by_status: dict[str, int]
    commitments_by_status: dict[str, int]
    commitments_by_type: dict[str, int]
    funding_committed_by_currency: dict[str, float]


class MLAnalytics(BaseModel):
    challenges_with_embedding: int
    clusters_with_embedding: int
    solutions_with_embedding: int
    duplicate_candidates_generated: int
    duplicate_decisions_total: int
    duplicate_decisions_by_type: dict[str, int]


class ModelInfo(BaseModel):
    model_name: str
    embedding_dimension: int
    duplicate_similarity_threshold: float
    duplicate_candidate_limit: int
    ml_service_url: str
