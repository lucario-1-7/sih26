import uuid

import pytest

from tests.conftest import auth_headers


async def _make_cluster(client, validator_user) -> str:
    resp = await client.post(
        "/api/v1/clusters",
        json={"title": f"Impact Test Cluster {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _make_project(client, coordinator_user, cluster_id: str) -> dict:
    resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"Impact Test Project {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_impact_indicator_baseline_endline_and_verification(
    client, validator_user, coordinator_user, faculty_user
):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)
    pid = project["id"]

    resp = await client.post(
        f"/api/v1/projects/{pid}/impact-indicators",
        json={"name": "pump_downtime_days", "unit": "days", "baseline_value": 20, "target_value": 2},
        headers=auth_headers(faculty_user),
    )
    assert resp.status_code == 201
    indicator = resp.json()
    assert indicator["baseline_value"] == 20
    assert indicator["actual_value"] is None
    assert indicator["verified_at"] is None

    resp = await client.patch(
        f"/api/v1/projects/{pid}/impact-indicators/{indicator['id']}/endline",
        json={"actual_value": 3, "endline_date": "2026-06-01", "endline_evidence": "Field survey report"},
        headers=auth_headers(faculty_user),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["actual_value"] == 3
    # Claimed, not yet verified.
    assert body["verified_at"] is None


@pytest.mark.asyncio
async def test_faculty_cannot_verify_impact_only_validator_or_superadmin_can(
    client, validator_user, coordinator_user, faculty_user
):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)
    pid = project["id"]

    resp = await client.post(
        f"/api/v1/projects/{pid}/impact-indicators",
        json={"name": "households_with_safe_water", "unit": "households"},
        headers=auth_headers(faculty_user),
    )
    indicator_id = resp.json()["id"]

    await client.patch(
        f"/api/v1/projects/{pid}/impact-indicators/{indicator_id}/endline",
        json={"actual_value": 120, "endline_date": "2026-06-01"},
        headers=auth_headers(faculty_user),
    )

    resp = await client.post(
        f"/api/v1/projects/{pid}/impact-indicators/{indicator_id}/verify",
        json={"approve": True},
        headers=auth_headers(faculty_user),
    )
    assert resp.status_code == 403

    resp = await client.post(
        f"/api/v1/projects/{pid}/impact-indicators/{indicator_id}/verify",
        json={"approve": True},
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["verified_at"] is not None
    assert body["verified_by_id"] == str(validator_user.id)


@pytest.mark.asyncio
async def test_cannot_verify_indicator_with_no_endline_claim(
    client, validator_user, coordinator_user, faculty_user
):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)
    pid = project["id"]

    resp = await client.post(
        f"/api/v1/projects/{pid}/impact-indicators",
        json={"name": "no_endline_yet", "unit": "count"},
        headers=auth_headers(faculty_user),
    )
    indicator_id = resp.json()["id"]

    resp = await client.post(
        f"/api/v1/projects/{pid}/impact-indicators/{indicator_id}/verify",
        json={"approve": True},
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_completing_a_project_does_not_verify_impact(client, validator_user, coordinator_user):
    """A project reaching COMPLETED must never imply verified impact."""
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)
    pid = project["id"]

    for target in ("accepted", "active", "completed"):
        resp = await client.patch(
            f"/api/v1/projects/{pid}", json={"status": target}, headers=auth_headers(coordinator_user)
        )
        assert resp.status_code == 200

    resp = await client.get(f"/api/v1/projects/{pid}/impact-indicators", headers=auth_headers(coordinator_user))
    assert resp.status_code == 200
    assert resp.json()["items"] == []


@pytest.mark.asyncio
async def test_analytics_requires_superadmin(client, validator_user, coordinator_user):
    resp = await client.get("/api/v1/analytics/challenges", headers=auth_headers(validator_user))
    assert resp.status_code == 403

    resp = await client.get("/api/v1/analytics/projects", headers=auth_headers(coordinator_user))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_analytics_endpoints_return_aggregated_counts(client, superadmin_user, citizen_user, administrative_area):
    resp = await client.post(
        "/api/v1/challenges",
        json={
            "title": "Analytics smoke test challenge",
            "description": "A challenge created purely to exercise the analytics aggregation endpoints.",
            "administrative_area_id": str(administrative_area.id),
        },
        headers=auth_headers(citizen_user),
    )
    assert resp.status_code == 201

    resp = await client.get("/api/v1/analytics/challenges", headers=auth_headers(superadmin_user))
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    assert isinstance(body["by_status"], dict)

    resp = await client.get("/api/v1/analytics/projects", headers=auth_headers(superadmin_user))
    assert resp.status_code == 200

    resp = await client.get("/api/v1/analytics/industry", headers=auth_headers(superadmin_user))
    assert resp.status_code == 200

    resp = await client.get("/api/v1/analytics/ml", headers=auth_headers(superadmin_user))
    assert resp.status_code == 200

    resp = await client.get("/api/v1/analytics/model-info", headers=auth_headers(superadmin_user))
    assert resp.status_code == 200
    info = resp.json()
    assert info["embedding_dimension"] == 384
