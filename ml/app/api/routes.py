from fastapi import APIRouter

from app.api.schemas import (
    ConsortiumRequest,
    ConsortiumResponse,
    DuplicateCandidatesRequest,
    DuplicateCandidatesResponse,
    EmbedRequest,
    EmbedResponse,
    MatchRankRequest,
    MatchRankResponse,
    ScoreRequestFieldIntensity,
    ScoreRequestPriority,
    ScoreRequestTractability,
    ScoreResponse,
)
from app.core.config import get_settings
from app.duplicate_detection.engine import EmbeddingRecord, find_duplicate_candidates
from app.embeddings.engine import embed
from app.matching.consortium import suggest_consortium
from app.matching.engine import MatchCandidate, rank_candidates
from app.scoring.field_intensity import score_field_intensity
from app.scoring.priority import score_priority
from app.scoring.tractability import score_tractability

router = APIRouter(prefix="/api/v1")


@router.post("/embeddings", response_model=EmbedResponse, summary="Embed text into a 384-dim vector")
def create_embedding(payload: EmbedRequest) -> EmbedResponse:
    settings = get_settings()
    vector = embed(payload.text)
    return EmbedResponse(embedding=vector, model_name=settings.ML_MODEL_NAME, dimension=len(vector))


@router.post(
    "/duplicate-candidates",
    response_model=DuplicateCandidatesResponse,
    summary="Rank candidates by similarity to a query embedding (evidence only, never a merge decision)",
)
def duplicate_candidates(payload: DuplicateCandidatesRequest) -> DuplicateCandidatesResponse:
    corpus = [EmbeddingRecord(id=c.id, embedding=c.embedding) for c in payload.candidates]
    ranked = find_duplicate_candidates(payload.query_embedding, corpus, threshold=payload.threshold)
    return DuplicateCandidatesResponse(
        ranked_candidates=[
            {
                "id": r.id,
                "similarity_score": r.similarity_score,
                "is_candidate": r.is_candidate,
                "model_name": r.model_name,
                "model_version": r.model_version,
            }
            for r in ranked
        ]
    )


@router.post(
    "/matching/rank",
    response_model=MatchRankResponse,
    summary="Rank organizations for a cluster/project by semantic + domain-tag match",
)
def matching_rank(payload: MatchRankRequest) -> MatchRankResponse:
    candidates = [
        MatchCandidate(id=c.id, embedding=c.embedding, domain_tags=c.domain_tags, type=c.type)
        for c in payload.candidates
    ]
    ranked = rank_candidates(payload.query_embedding, payload.query_domain_tags, candidates)
    return MatchRankResponse(
        ranked_matches=[
            {"id": r.id, "score": r.score, "breakdown": r.breakdown, "rationale": r.rationale, "type": r.type}
            for r in ranked
        ]
    )


@router.post(
    "/matching/consortium",
    response_model=ConsortiumResponse,
    summary="Suggest consortium composition from ranked matches (suggestion only; backend owns persistence)",
)
def matching_consortium(payload: ConsortiumRequest) -> ConsortiumResponse:
    from app.matching.engine import RankedMatch

    ranked = [
        RankedMatch(id=m.id, score=m.score, breakdown=m.breakdown, rationale=m.rationale, type=m.type)
        for m in payload.ranked_matches
    ]
    suggestions = suggest_consortium(ranked, payload.team_size)
    return ConsortiumResponse(
        members=[
            {"organization_id": s.organization_id, "role": s.role, "score": s.score, "rationale": s.rationale}
            for s in suggestions
        ]
    )


@router.post(
    "/scoring/field-intensity", response_model=ScoreResponse, summary="Score challenge field intensity"
)
def scoring_field_intensity(payload: ScoreRequestFieldIntensity) -> ScoreResponse:
    result = score_field_intensity(**payload.model_dump())
    return ScoreResponse(**result.__dict__)


@router.post("/scoring/priority", response_model=ScoreResponse, summary="Score cluster priority")
def scoring_priority(payload: ScoreRequestPriority) -> ScoreResponse:
    result = score_priority(**payload.model_dump())
    return ScoreResponse(**result.__dict__)


@router.post("/scoring/tractability", response_model=ScoreResponse, summary="Score cluster tractability")
def scoring_tractability(payload: ScoreRequestTractability) -> ScoreResponse:
    result = score_tractability(**payload.model_dump())
    return ScoreResponse(**result.__dict__)
