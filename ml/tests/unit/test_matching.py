from app.embeddings.engine import embed
from app.matching.engine import MatchCandidate, rank_candidates


def test_matching_ranks_semantic_and_tag_similarity_higher():
    query = embed("flood control and drainage infrastructure")
    close = embed("flood control and drainage system upgrade")
    far = embed("music festival ticket booking")

    candidates = [
        MatchCandidate(id="close", embedding=close, domain_tags=["water"], type="university"),
        MatchCandidate(id="far", embedding=far, domain_tags=["arts"], type="industry"),
    ]
    ranked = rank_candidates(query, ["water", "infrastructure"], candidates)

    assert ranked[0].id == "close"
    assert ranked[0].score > ranked[1].score
    assert "semantic_similarity" in ranked[0].breakdown
    assert "domain_tag_overlap" in ranked[0].breakdown
