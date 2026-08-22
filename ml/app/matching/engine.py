from dataclasses import dataclass

from app.duplicate_detection.engine import _cosine_similarity

SEMANTIC_WEIGHT = 0.7
DOMAIN_TAG_WEIGHT = 0.3


@dataclass
class MatchCandidate:
    id: str
    embedding: list[float]
    domain_tags: list[str]
    type: str | None = None


@dataclass
class RankedMatch:
    id: str
    score: float
    breakdown: dict[str, float]
    rationale: str
    type: str | None = None


def _tag_overlap(a: list[str], b: list[str]) -> float:
    set_a, set_b = {t.lower() for t in a}, {t.lower() for t in b}
    if not set_a and not set_b:
        return 0.0
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def rank_candidates(
    query_embedding: list[float],
    query_domain_tags: list[str],
    candidates: list[MatchCandidate],
) -> list[RankedMatch]:
    """Explainable semantic + domain-tag matching. Never guarantees suitability —
    scores are a ranking aid for a human decision-maker."""
    results = []
    for candidate in candidates:
        similarity = _cosine_similarity(query_embedding, candidate.embedding)
        overlap = _tag_overlap(query_domain_tags, candidate.domain_tags)
        breakdown = {
            "semantic_similarity": SEMANTIC_WEIGHT * similarity,
            "domain_tag_overlap": DOMAIN_TAG_WEIGHT * overlap,
        }
        score = sum(breakdown.values())
        rationale = (
            f"Semantic similarity {similarity:.2f}, domain tag overlap {overlap:.2f} "
            f"(weights: semantic={SEMANTIC_WEIGHT}, tags={DOMAIN_TAG_WEIGHT})."
        )
        results.append(
            RankedMatch(id=candidate.id, score=score, breakdown=breakdown, rationale=rationale, type=candidate.type)
        )
    results.sort(key=lambda r: r.score, reverse=True)
    return results
