from app.scoring.field_intensity import score_field_intensity
from app.scoring.priority import score_priority
from app.scoring.tractability import score_tractability


def test_field_intensity_returns_breakdown_and_weight_version():
    result = score_field_intensity(frequency=0.8, severity=0.9, recency_days=2, geographic_spread=0.4)
    assert 0.0 <= result.score <= 1.0
    assert set(result.breakdown) == {"frequency", "severity", "recency", "geographic_spread"}
    assert result.weight_version == "v1"


def test_priority_breakdown_nonempty():
    result = score_priority(field_intensity=0.7, community_impact=0.6, cluster_size=10)
    assert result.breakdown
    assert 0.0 <= result.score <= 1.0


def test_tractability_complexity_penalizes_score():
    low_complexity = score_tractability(
        resource_availability=0.5, historical_resolution_rate=0.5, complexity=0.1
    )
    high_complexity = score_tractability(
        resource_availability=0.5, historical_resolution_rate=0.5, complexity=0.9
    )
    assert high_complexity.score < low_complexity.score
