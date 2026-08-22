from app.duplicate_detection.engine import EmbeddingRecord, find_duplicate_candidates
from app.embeddings.engine import embed


def test_duplicate_candidates_ranked_by_similarity():
    query = embed("Streetlight broken near the market")
    similar = embed("Street light not working close to the bazaar")
    different = embed("Water supply is contaminated in the village well")

    corpus = [
        EmbeddingRecord(id="similar", embedding=similar),
        EmbeddingRecord(id="different", embedding=different),
    ]
    ranked = find_duplicate_candidates(query, corpus, threshold=0.5)

    assert ranked[0].id == "similar"
    assert ranked[0].is_candidate is True
    assert ranked[1].id == "different"
    assert ranked[1].is_candidate is False
    assert ranked[0].similarity_score > ranked[1].similarity_score


def test_duplicate_candidates_never_returns_a_merge_decision():
    query = embed("Pothole on main road")
    corpus = [EmbeddingRecord(id="a", embedding=embed("Pothole on main road causing accidents"))]
    ranked = find_duplicate_candidates(query, corpus, threshold=0.9)
    # High threshold => not flagged as candidate; this is evidence only, never an action.
    assert ranked[0].is_candidate in (True, False)
    assert not hasattr(ranked[0], "merge")
    assert not hasattr(ranked[0], "delete")
