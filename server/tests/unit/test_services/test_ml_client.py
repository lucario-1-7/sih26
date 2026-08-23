"""Unit tests for the ml_client HTTP contract-validation hardening.

Exercises ml_client against an httpx.MockTransport (no real network, no real
ML container) so every response shape — valid, missing field, wrong type,
malformed JSON, unexpected enum, invalid score, 500, timeout, unreachable —
can be asserted deterministically. This complements (does not replace) the
integration tests that hit the real, live ML container.
"""

import httpx
import pytest

from app.services import ml_client
from app.services.ml_client import MLServiceError


def _patch_client(monkeypatch, handler):
    def _client() -> httpx.AsyncClient:
        transport = httpx.MockTransport(handler)
        return httpx.AsyncClient(transport=transport, base_url="http://ml-test")

    monkeypatch.setattr(ml_client, "_client", _client)


@pytest.mark.asyncio
async def test_embed_text_valid_response(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"embedding": [0.1, 0.2, 0.3]})

    _patch_client(monkeypatch, handler)
    result = await ml_client.embed_text("hello")
    assert result == [0.1, 0.2, 0.3]


@pytest.mark.asyncio
async def test_embed_text_missing_required_field_raises_ml_service_error(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"model_name": "x", "dimension": 3})  # no "embedding"

    _patch_client(monkeypatch, handler)
    with pytest.raises(MLServiceError):
        await ml_client.embed_text("hello")


@pytest.mark.asyncio
async def test_embed_text_wrong_field_type_raises_ml_service_error(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"embedding": "not-a-list"})

    _patch_client(monkeypatch, handler)
    with pytest.raises(MLServiceError):
        await ml_client.embed_text("hello")


@pytest.mark.asyncio
async def test_embed_text_malformed_json_raises_ml_service_error(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"{not valid json", headers={"content-type": "application/json"})

    _patch_client(monkeypatch, handler)
    with pytest.raises(MLServiceError):
        await ml_client.embed_text("hello")


@pytest.mark.asyncio
async def test_classify_domain_unexpected_confidence_out_of_range_raises(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "domain": "water",
                "confidence": 1.7,  # far out of [0, 1] — a real contract violation, not float noise
                "alternatives": [],
                "needs_review": False,
                "source": "trained",
                "model_version": "v1",
            },
        )

    _patch_client(monkeypatch, handler)
    with pytest.raises(MLServiceError):
        await ml_client.classify_domain([0.1, 0.2])


@pytest.mark.asyncio
async def test_classify_domain_unexpected_shape_for_alternatives_raises(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "domain": "water",
                "confidence": 0.9,
                "alternatives": "not-a-list",  # wrong type
                "needs_review": False,
                "source": "trained",
                "model_version": "v1",
            },
        )

    _patch_client(monkeypatch, handler)
    with pytest.raises(MLServiceError):
        await ml_client.classify_domain([0.1, 0.2])


@pytest.mark.asyncio
async def test_classify_field_intensity_valid_fallback_response_is_surfaced_explicitly(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "field_intensity": 0.5,
                "label": "HYBRID",
                "needs_review": True,
                "source": "rules_fallback",
                "model_version": "fallback",
            },
        )

    _patch_client(monkeypatch, handler)
    result = await ml_client.classify_field_intensity("text", "water", [0.1])
    # The fallback must be surfaced explicitly, never disguised as "trained".
    assert result["source"] == "rules_fallback"
    assert result["needs_review"] is True


@pytest.mark.asyncio
async def test_ml_500_raises_ml_service_error_not_httpx_exception(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"detail": "internal error"})

    _patch_client(monkeypatch, handler)
    with pytest.raises(MLServiceError):
        await ml_client.embed_text("hello")


@pytest.mark.asyncio
async def test_ml_timeout_raises_ml_service_error(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out", request=request)

    _patch_client(monkeypatch, handler)
    with pytest.raises(MLServiceError):
        await ml_client.embed_text("hello")


@pytest.mark.asyncio
async def test_ml_unreachable_raises_ml_service_error(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    _patch_client(monkeypatch, handler)
    with pytest.raises(MLServiceError):
        await ml_client.embed_text("hello")


@pytest.mark.asyncio
async def test_rank_duplicate_candidates_bad_similarity_score_raises(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "ranked_candidates": [
                    {
                        "id": "abc",
                        "similarity_score": 42.0,  # out of [0, 1] — contract violation
                        "is_candidate": True,
                        "model_name": "x",
                        "model_version": "1",
                    }
                ]
            },
        )

    _patch_client(monkeypatch, handler)
    with pytest.raises(MLServiceError):
        await ml_client.rank_duplicate_candidates(query_embedding=[0.1], candidates=[], threshold=0.8)


@pytest.mark.asyncio
async def test_no_raw_keyerror_or_json_error_ever_escapes_ml_client(monkeypatch):
    """The exact regression this hardening exists for: a malformed ML response
    used to raise a raw KeyError/JSONDecodeError instead of MLServiceError."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"totally": "unexpected shape"})

    _patch_client(monkeypatch, handler)
    try:
        await ml_client.rank_matches(query_embedding=[0.1], query_domain_tags=[], candidates=[])
        assert False, "expected MLServiceError"
    except MLServiceError:
        pass
    except (KeyError, ValueError) as exc:
        pytest.fail(f"a raw {type(exc).__name__} escaped ml_client instead of MLServiceError: {exc}")
