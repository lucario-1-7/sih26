import httpx

from app.core.config import get_settings


class MLServiceError(Exception):
    """The ML service could not be reached, timed out, or returned an error.
    Mapped to an HTTP 503 by the global exception handler (see app.core.errors)
    — callers should let this propagate rather than catching it themselves."""


def _to_list(embedding) -> list[float]:
    """pgvector deserializes Vector columns as numpy arrays; JSON needs plain lists."""
    return embedding.tolist() if hasattr(embedding, "tolist") else list(embedding)


def _client() -> httpx.AsyncClient:
    settings = get_settings()
    return httpx.AsyncClient(base_url=settings.ML_SERVICE_URL, timeout=settings.ML_SERVICE_TIMEOUT_SECONDS)


async def embed_text(text: str) -> list[float]:
    """Returns a plain Python list — safe to assign directly to a pgvector column."""
    async with _client() as client:
        try:
            resp = await client.post("/api/v1/embeddings", json={"text": text})
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise MLServiceError(f"embedding request failed: {exc}") from exc
    return resp.json()["embedding"]


async def rank_duplicate_candidates(
    *,
    query_embedding: list[float],
    candidates: list[dict],
    threshold: float,
) -> list[dict]:
    """candidates: list of {"id": str, "embedding": list[float]}."""
    payload_candidates = [{**c, "embedding": _to_list(c["embedding"])} for c in candidates]
    async with _client() as client:
        try:
            resp = await client.post(
                "/api/v1/duplicate-candidates",
                json={
                    "query_embedding": _to_list(query_embedding),
                    "candidates": payload_candidates,
                    "threshold": threshold,
                },
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise MLServiceError(f"duplicate-candidates request failed: {exc}") from exc
    return resp.json()["ranked_candidates"]


async def rank_matches(
    *,
    query_embedding: list[float],
    query_domain_tags: list[str],
    candidates: list[dict],
) -> list[dict]:
    """candidates: list of {"id": str, "embedding": list[float], "domain_tags": list[str], "type": str}."""
    payload_candidates = [{**c, "embedding": _to_list(c["embedding"])} for c in candidates]
    async with _client() as client:
        try:
            resp = await client.post(
                "/api/v1/matching/rank",
                json={
                    "query_embedding": _to_list(query_embedding),
                    "query_domain_tags": query_domain_tags,
                    "candidates": payload_candidates,
                },
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise MLServiceError(f"matching rank request failed: {exc}") from exc
    return resp.json()["ranked_matches"]


async def suggest_consortium(*, ranked_matches: list[dict], team_size: int) -> list[dict]:
    async with _client() as client:
        try:
            resp = await client.post(
                "/api/v1/matching/consortium",
                json={"ranked_matches": ranked_matches, "team_size": team_size},
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise MLServiceError(f"consortium suggestion request failed: {exc}") from exc
    return resp.json()["members"]
