from app.scoring.models import ScoredResult
from app.scoring.weights import CURRENT_WEIGHT_VERSION, get_weights


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def score_priority(
    *,
    field_intensity: float,
    community_impact: float,
    cluster_size: int,
    max_cluster_size_reference: int = 50,
    weight_version: str = CURRENT_WEIGHT_VERSION,
) -> ScoredResult:
    """Combine field intensity, community impact, and cluster size into a priority score."""
    weights = get_weights("priority", weight_version)
    cluster_size_signal = _clamp01(cluster_size / max(1, max_cluster_size_reference))

    breakdown = {
        "field_intensity": weights["field_intensity"] * _clamp01(field_intensity),
        "community_impact": weights["community_impact"] * _clamp01(community_impact),
        "cluster_size": weights["cluster_size"] * cluster_size_signal,
    }
    score = sum(breakdown.values())
    rationale = (
        f"Weighted combination of field intensity, community impact, and relative cluster "
        f"size using weight set {weight_version}."
    )
    return ScoredResult(score=score, breakdown=breakdown, rationale=rationale, weight_version=weight_version)
