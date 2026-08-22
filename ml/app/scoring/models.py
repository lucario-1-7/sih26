from dataclasses import dataclass, field


@dataclass
class ScoredResult:
    score: float
    breakdown: dict[str, float]
    rationale: str
    weight_version: str
