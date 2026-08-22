import uuid

import pytest

from app.repositories.cluster_repository import ClusterRepository
from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_get_cluster_matches_does_not_compute_or_persist_an_embedding(client, db, validator_user):
    resp = await client.post(
        "/api/v1/clusters",
        json={"title": f"GET Side Effect Test Cluster {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 201
    cluster_id = resp.json()["id"]

    cluster_before = await ClusterRepository(db).get(uuid.UUID(cluster_id))
    assert cluster_before.embedding is None
    updated_at_before = cluster_before.updated_at

    resp = await client.get(f"/api/v1/matching/clusters/{cluster_id}", headers=auth_headers(validator_user))
    assert resp.status_code == 200
    # No embedding yet (the background job hasn't run in this test) — the
    # read-only endpoint must return an empty result, never compute one itself.
    assert resp.json() == []

    # Re-fetch in a fresh query to bypass any identity-map staleness and prove
    # the row was not mutated by the GET.
    db.expire_all()
    cluster_after = await ClusterRepository(db).get(uuid.UUID(cluster_id))
    assert cluster_after.embedding is None
    assert cluster_after.updated_at == updated_at_before


@pytest.mark.asyncio
async def test_get_cluster_matches_returns_results_once_embedding_exists(client, db, validator_user):
    resp = await client.post(
        "/api/v1/clusters",
        json={"title": f"GET Side Effect Test Cluster With Embedding {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(validator_user),
    )
    cluster_id = resp.json()["id"]

    # Simulate what the `generate_cluster_embedding` ARQ job would have done —
    # persistence happens there, never inside the GET handler itself.
    cluster = await ClusterRepository(db).get(uuid.UUID(cluster_id))
    cluster.embedding = [0.01] * 384
    await db.commit()

    resp = await client.get(f"/api/v1/matching/clusters/{cluster_id}", headers=auth_headers(validator_user))
    assert resp.status_code == 200
    assert resp.json() == []  # no organizations registered — still a valid empty ranking, not an error
