from dataclasses import dataclass

from app.matching.engine import RankedMatch

ROLE_BY_TYPE = {
    "university": "research_partner",
    "industry": "industry_partner",
}
DEFAULT_ROLE = "partner"


@dataclass
class ConsortiumMemberSuggestion:
    organization_id: str
    role: str
    score: float
    rationale: str


def suggest_consortium(
    ranked_matches: list[RankedMatch], team_size: int
) -> list[ConsortiumMemberSuggestion]:
    """Rank potential participants into a consortium suggestion.

    This suggests composition only — the backend owns persistence, membership
    confirmation, and lifecycle. Nothing here mutates any consortium record.
    """
    top = sorted(ranked_matches, key=lambda m: m.score, reverse=True)[:team_size]
    return [
        ConsortiumMemberSuggestion(
            organization_id=match.id,
            role=ROLE_BY_TYPE.get(match.type or "", DEFAULT_ROLE),
            score=match.score,
            rationale=match.rationale,
        )
        for match in top
    ]
