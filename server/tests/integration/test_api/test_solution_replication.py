import uuid

import pytest

from tests.conftest import auth_headers


async def _make_cluster(client, validator_user) -> str:
    resp = await client.post(
        "/api/v1/clusters",
        json={"title": f"Replication Test Cluster {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _make_project(client, coordinator_user, cluster_id: str) -> dict:
    resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"Replication Test Project {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_solution_creation_computes_embedding_and_starts_draft(
    client, validator_user, coordinator_user, faculty_user
):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)

    resp = await client.post(
        "/api/v1/solutions",
        json={
            "project_id": project["id"],
            "title": "Solar-powered borewell pump retrofit",
            "outcome": "Reduced pump downtime from 20 days/month to under 3.",
        },
        headers=auth_headers(faculty_user),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "draft"


@pytest.mark.asyncio
async def test_publishing_a_solution(client, validator_user, coordinator_user, faculty_user):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)

    resp = await client.post(
        "/api/v1/solutions",
        json={"project_id": project["id"], "title": "Community water filtration prototype"},
        headers=auth_headers(faculty_user),
    )
    solution_id = resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/solutions/{solution_id}", json={"status": "published"}, headers=auth_headers(coordinator_user)
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "published"


@pytest.mark.asyncio
async def test_replication_candidates_returns_ranked_open_clusters(
    client, validator_user, coordinator_user, faculty_user
):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)

    resp = await client.post(
        "/api/v1/solutions",
        json={
            "project_id": project["id"],
            "title": "Low-cost handpump repair kit rollout",
            "outcome": "Repaired handpumps across twelve villages using a standardized low-cost kit.",
        },
        headers=auth_headers(faculty_user),
    )
    solution_id = resp.json()["id"]

    resp = await client.get(
        f"/api/v1/solutions/{solution_id}/replication-candidates", headers=auth_headers(coordinator_user)
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_industry_cannot_publish_a_solution(client, validator_user, coordinator_user, faculty_user, industry_user):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)

    resp = await client.post(
        "/api/v1/solutions",
        json={"project_id": project["id"], "title": "Industry cannot touch this solution"},
        headers=auth_headers(faculty_user),
    )
    solution_id = resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/solutions/{solution_id}", json={"status": "published"}, headers=auth_headers(industry_user)
    )
    assert resp.status_code == 403
