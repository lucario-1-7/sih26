"""Versioned scoring weight configs.

A weight set, once used in production scoring, must never be edited in place —
add a new version key instead. `CURRENT_WEIGHT_VERSION` selects the default for
new scoring runs; every ScoredResult records which version produced it.
"""

WEIGHT_CONFIGS: dict[str, dict[str, dict[str, float]]] = {
    "v1": {
        "field_intensity": {"frequency": 0.35, "severity": 0.35, "recency": 0.15, "geographic_spread": 0.15},
        "priority": {"field_intensity": 0.5, "community_impact": 0.3, "cluster_size": 0.2},
        "tractability": {
            "resource_availability": 0.4,
            "historical_resolution_rate": 0.35,
            "complexity_penalty": 0.25,
        },
    }
}

CURRENT_WEIGHT_VERSION = "v1"


def get_weights(category: str, version: str = CURRENT_WEIGHT_VERSION) -> dict[str, float]:
    return dict(WEIGHT_CONFIGS[version][category])
