from app.matching.consortium import suggest_consortium
from app.matching.engine import RankedMatch


def test_consortium_respects_team_size_and_assigns_role_by_type():
    matches = [
        RankedMatch(id="u1", score=0.9, breakdown={"x": 0.9}, rationale="r1", type="university"),
        RankedMatch(id="i1", score=0.8, breakdown={"x": 0.8}, rationale="r2", type="industry"),
        RankedMatch(id="i2", score=0.1, breakdown={"x": 0.1}, rationale="r3", type="industry"),
    ]
    suggestion = suggest_consortium(matches, team_size=2)

    assert len(suggestion) == 2
    assert suggestion[0].organization_id == "u1"
    assert suggestion[0].role == "research_partner"
    assert suggestion[1].organization_id == "i1"
    assert suggestion[1].role == "industry_partner"


def test_consortium_does_not_mutate_input():
    matches = [RankedMatch(id="u1", score=0.5, breakdown={}, rationale="r", type="university")]
    before = list(matches)
    suggest_consortium(matches, team_size=1)
    assert matches == before
