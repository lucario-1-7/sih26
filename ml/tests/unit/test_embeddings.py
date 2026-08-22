from app.embeddings.engine import embed, embed_batch


def test_embedding_dimension():
    result = embed("The road is damaged near the school")
    assert len(result) == 384
    assert all(isinstance(x, float) for x in result)


def test_embedding_multilingual():
    en = embed("The road is damaged")
    hi = embed("सड़क क्षतिग्रस्त है")
    assert len(en) == 384
    assert len(hi) == 384


def test_embed_batch_matches_single():
    texts = ["first challenge report", "second challenge report"]
    batch = embed_batch(texts)
    assert len(batch) == 2
    assert all(len(v) == 384 for v in batch)
