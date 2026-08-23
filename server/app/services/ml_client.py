import json
import logging

import httpx
from pydantic import BaseModel, Field, ValidationError

from app.core.config import get_settings

logger = logging.getLogger("app.ml_client")

# Cosine similarity and softmax-derived confidences are mathematically bounded
# to [0, 1], but float64 dot products on near-identical normalized vectors can
# land a hair over 1.0 (e.g. 1.0000000000000002). A strict le=1.0 would reject
# that as a contract violation even though it is a correct, healthy response —
# so probability-like fields get a small numerical-precision tolerance instead
# of a hard bound.
_PROB_EPSILON = 1e-6


class MLServiceError(Exception):
    """The ML service could not be reached, timed out, returned an error status,
    or returned a response that does not match its documented contract (missing
    field, wrong type, malformed JSON). Mapped to an HTTP 503 by the global
    exception handler (see app.core.errors) — callers should let this
    propagate rather than catching it themselves."""


# --- Response contracts -----------------------------------------------------
# Mirrors ml/app/api/schemas.py. Validating here means a malformed or
# schema-drifted ML response becomes a clean MLServiceError/503 instead of a
# raw KeyError or type error leaking out of this module.


class _EmbedResponse(BaseModel):
    embedding: list[float]


class _DuplicateCandidateOut(BaseModel):
    id: str
    similarity_score: float = Field(ge=0.0, le=1.0 + _PROB_EPSILON)
    is_candidate: bool
    model_name: str
    model_version: str


class _DuplicateCandidatesResponse(BaseModel):
    ranked_candidates: list[_DuplicateCandidateOut]


class _RankedMatchOut(BaseModel):
    id: str
    score: float
    breakdown: dict[str, float]
    rationale: str
    type: str | None = None


class _MatchRankResponse(BaseModel):
    ranked_matches: list[_RankedMatchOut]


class _ConsortiumMemberOut(BaseModel):
    organization_id: str
    role: str
    score: float
    rationale: str


class _ConsortiumResponse(BaseModel):
    members: list[_ConsortiumMemberOut]


class _DomainAlternativeOut(BaseModel):
    domain: str
    confidence: float = Field(ge=0.0, le=1.0 + _PROB_EPSILON)


class _DomainClassifyResponse(BaseModel):
    domain: str
    confidence: float = Field(ge=0.0, le=1.0 + _PROB_EPSILON)
    alternatives: list[_DomainAlternativeOut]
    needs_review: bool
    source: str
    model_version: str


class _FieldClassifyResponse(BaseModel):
    field_intensity: float = Field(ge=0.0, le=1.0 + _PROB_EPSILON)
    label: str
    needs_review: bool
    source: str
    model_version: str


def _to_list(embedding) -> list[float]:
    """pgvector deserializes Vector columns as numpy arrays; JSON needs plain lists."""
    return embedding.tolist() if hasattr(embedding, "tolist") else list(embedding)


def _client() -> httpx.AsyncClient:
    settings = get_settings()
    return httpx.AsyncClient(base_url=settings.ML_SERVICE_URL, timeout=settings.ML_SERVICE_TIMEOUT_SECONDS)


async def _post(client: httpx.AsyncClient, path: str, payload: dict) -> httpx.Response:
    try:
        resp = await client.post(path, json=payload)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise MLServiceError(f"{path} request failed: {exc}") from exc
    return resp


def _validate(response_model: type[BaseModel], resp: httpx.Response, path: str) -> BaseModel:
    """Parses and validates resp against response_model. Never lets a raw
    JSONDecodeError or pydantic ValidationError escape this module — both
    indicate the ML service returned something outside its documented
    contract, which callers must treat the same as it being unavailable."""
    try:
        data = resp.json()
    except json.JSONDecodeError as exc:
        raise MLServiceError(f"{path} returned malformed JSON: {exc}") from exc
    try:
        return response_model.model_validate(data)
    except ValidationError as exc:
        logger.error("ml_response_contract_violation path=%s errors=%s", path, exc.errors())
        raise MLServiceError(f"{path} response failed contract validation: {exc}") from exc


async def embed_text(text: str) -> list[float]:
    """Returns a plain Python list — safe to assign directly to a pgvector column."""
    async with _client() as client:
        resp = await _post(client, "/api/v1/embeddings", {"text": text})
    return _validate(_EmbedResponse, resp, "/api/v1/embeddings").embedding


async def classify_domain(embedding: list[float]) -> dict:
    """Advisory civic-domain classification for a challenge. Never authoritative
    — callers must treat the result as a suggestion, not a decision."""
    async with _client() as client:
        resp = await _post(client, "/api/v1/classify-domain", {"embedding": _to_list(embedding)})
    return _validate(_DomainClassifyResponse, resp, "/api/v1/classify-domain").model_dump()


async def classify_field_intensity(text: str, domain: str, embedding: list[float]) -> dict:
    """Advisory physical-vs-remote classification for a challenge. Never
    authoritative — callers must treat the result as a suggestion, not a decision."""
    async with _client() as client:
        resp = await _post(
            client,
            "/api/v1/classify-field-intensity",
            {"text": text, "domain": domain, "embedding": _to_list(embedding)},
        )
    return _validate(_FieldClassifyResponse, resp, "/api/v1/classify-field-intensity").model_dump()


async def rank_duplicate_candidates(
    *,
    query_embedding: list[float],
    candidates: list[dict],
    threshold: float,
) -> list[dict]:
    """candidates: list of {"id": str, "embedding": list[float]}."""
    payload_candidates = [{**c, "embedding": _to_list(c["embedding"])} for c in candidates]
    async with _client() as client:
        resp = await _post(
            client,
            "/api/v1/duplicate-candidates",
            {
                "query_embedding": _to_list(query_embedding),
                "candidates": payload_candidates,
                "threshold": threshold,
            },
        )
    validated = _validate(_DuplicateCandidatesResponse, resp, "/api/v1/duplicate-candidates")
    return [c.model_dump() for c in validated.ranked_candidates]


async def rank_matches(
    *,
    query_embedding: list[float],
    query_domain_tags: list[str],
    candidates: list[dict],
) -> list[dict]:
    """candidates: list of {"id": str, "embedding": list[float], "domain_tags": list[str], "type": str}."""
    payload_candidates = [{**c, "embedding": _to_list(c["embedding"])} for c in candidates]
    async with _client() as client:
        resp = await _post(
            client,
            "/api/v1/matching/rank",
            {
                "query_embedding": _to_list(query_embedding),
                "query_domain_tags": query_domain_tags,
                "candidates": payload_candidates,
            },
        )
    validated = _validate(_MatchRankResponse, resp, "/api/v1/matching/rank")
    return [m.model_dump() for m in validated.ranked_matches]


async def suggest_consortium(*, ranked_matches: list[dict], team_size: int) -> list[dict]:
    async with _client() as client:
        resp = await _post(
            client,
            "/api/v1/matching/consortium",
            {"ranked_matches": ranked_matches, "team_size": team_size},
        )
    validated = _validate(_ConsortiumResponse, resp, "/api/v1/matching/consortium")
    return [m.model_dump() for m in validated.members]
