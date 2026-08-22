from app.scoring.models import ScoredResult
from app.scoring.weights import CURRENT_WEIGHT_VERSION, get_weights


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def score_field_intensity(
    *,
    frequency: float,
    severity: float,
    recency_days: float,
    geographic_spread: float,
    weight_version: str = CURRENT_WEIGHT_VERSION,
) -> ScoredResult:
    """Score challenge urgency from field signals.

    frequency, severity, geographic_spread are expected pre-normalized to [0, 1].
    recency_days is converted to a [0, 1] recency signal (more recent -> higher).
    """
    weights = get_weights("field_intensity", weight_version)
    recency_signal = _clamp01(1.0 / (1.0 + recency_days / 30.0))

    breakdown = {
        "frequency": weights["frequency"] * _clamp01(frequency),
        "severity": weights["severity"] * _clamp01(severity),
        "recency": weights["recency"] * recency_signal,
        "geographic_spread": weights["geographic_spread"] * _clamp01(geographic_spread),
    }
    score = sum(breakdown.values())
    rationale = (
        f"Weighted combination of frequency, severity, recency, and geographic spread "
        f"using weight set {weight_version}."
    )
    return ScoredResult(score=score, breakdown=breakdown, rationale=rationale, weight_version=weight_version)
