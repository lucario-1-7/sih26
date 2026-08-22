from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_embeddings_endpoint():
    resp = client.post("/api/v1/embeddings", json={"text": "Broken water pipeline"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["dimension"] == 384
    assert len(body["embedding"]) == 384


def test_duplicate_candidates_endpoint():
    e1 = client.post("/api/v1/embeddings", json={"text": "Broken water pipeline near school"}).json()[
        "embedding"
    ]
    e2 = client.post(
        "/api/v1/embeddings", json={"text": "Water pipeline damaged close to the school"}
    ).json()["embedding"]

    resp = client.post(
        "/api/v1/duplicate-candidates",
        json={"query_embedding": e1, "candidates": [{"id": "c1", "embedding": e2}], "threshold": 0.5},
    )
    assert resp.status_code == 200
    ranked = resp.json()["ranked_candidates"]
    assert ranked[0]["id"] == "c1"
    assert ranked[0]["is_candidate"] is True


def test_scoring_endpoint_rejects_out_of_range_input():
    resp = client.post(
        "/api/v1/scoring/field-intensity",
        json={"frequency": 1.5, "severity": 0.5, "recency_days": 1, "geographic_spread": 0.5},
    )
    assert resp.status_code == 422
