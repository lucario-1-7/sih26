from app.scoring.models import ScoredResult
from app.scoring.weights import CURRENT_WEIGHT_VERSION, get_weights


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def score_tractability(
    *,
    resource_availability: float,
    historical_resolution_rate: float,
    complexity: float,
    weight_version: str = CURRENT_WEIGHT_VERSION,
) -> ScoredResult:
    """Estimate feasibility of resolving a cluster given resources and history.

    resource_availability, historical_resolution_rate, complexity are in [0, 1];
    higher complexity reduces tractability (applied as a penalty).
    """
    weights = get_weights("tractability", weight_version)

    breakdown = {
        "resource_availability": weights["resource_availability"] * _clamp01(resource_availability),
        "historical_resolution_rate": weights["historical_resolution_rate"]
        * _clamp01(historical_resolution_rate),
        "complexity_penalty": -weights["complexity_penalty"] * _clamp01(complexity),
    }
    score = _clamp01(sum(breakdown.values()))
    rationale = (
        f"Resource availability and historical resolution rate offset by a complexity "
        f"penalty, using weight set {weight_version}."
    )
    return ScoredResult(score=score, breakdown=breakdown, rationale=rationale, weight_version=weight_version)
