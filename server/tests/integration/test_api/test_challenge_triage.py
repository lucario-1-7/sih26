"""Regression coverage for the Challenge -> Cluster -> Project visibility
pipeline. A brand-new citizen challenge only becomes visible to
University/Industry (via a Project) once a VALIDATOR clusters it and a
COORDINATOR/SUPERADMIN turns that cluster into a project, see
challenge_service.update_challenge and the `/challenges?unclustered=true`
triage queue. These tests prove each real step of that pipeline actually
works end-to-end through the real API, not through mocked/fake state.
"""

import uuid

import pytest

from tests.conftest import auth_headers


async def _submit_challenge(client, citizen_user, administrative_area) -> str:
    resp = await client.post(
        "/api/v1/challenges",
        json={
            "title": f"Broken streetlight on Main Road {uuid.uuid4().hex[:8]}",
            "description": "The streetlight outside the community hall has been dark for two weeks now.",
            "administrative_area_id": str(administrative_area.id),
        },
        headers=auth_headers(citizen_user),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_new_challenge_is_persisted_and_immediately_visible_unauthenticated_to_government(
    client, citizen_user, administrative_area
):
    """Government's Challenges page (GET /challenges, no filter) already
    works: a brand-new challenge shows up there with zero extra steps."""
    challenge_id = await _submit_challenge(client, citizen_user, administrative_area)

    resp = await client.get("/api/v1/challenges", params={"limit": 100})
    assert resp.status_code == 200
    ids = {c["id"] for c in resp.json()["items"]}
    assert challenge_id in ids


@pytest.mark.asyncio
async def test_new_challenge_appears_in_the_unclustered_triage_queue(
    client, citizen_user, administrative_area
):
    challenge_id = await _submit_challenge(client, citizen_user, administrative_area)

    resp = await client.get("/api/v1/challenges", params={"unclustered": "true", "limit": 100})
    assert resp.status_code == 200
    ids = {c["id"] for c in resp.json()["items"]}
    assert challenge_id in ids


@pytest.mark.asyncio
async def test_validator_can_cluster_a_challenge_and_it_leaves_the_triage_queue(
    client, citizen_user, validator_user, administrative_area
):
    challenge_id = await _submit_challenge(client, citizen_user, administrative_area)

    cluster_resp = await client.post(
        "/api/v1/clusters",
        json={"title": f"Streetlight outages {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(validator_user),
    )
    assert cluster_resp.status_code == 201
    cluster_id = cluster_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/v1/challenges/{challenge_id}",
        json={"cluster_id": cluster_id},
        headers=auth_headers(validator_user),
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["cluster_id"] == cluster_id

    triage_resp = await client.get("/api/v1/challenges", params={"unclustered": "true", "limit": 100})
    assert challenge_id not in {c["id"] for c in triage_resp.json()["items"]}

    by_cluster_resp = await client.get("/api/v1/challenges", params={"cluster_id": cluster_id})
    assert challenge_id in {c["id"] for c in by_cluster_resp.json()["items"]}


@pytest.mark.asyncio
async def test_challenge_reaches_university_only_after_becoming_a_project(
    client, citizen_user, validator_user, coordinator_user, administrative_area, university_org
):
    """The actual end-to-end pipeline a University Coordinator's dashboard
    depends on: Challenge -> (validator) Cluster -> (coordinator) Project."""
    challenge_id = await _submit_challenge(client, citizen_user, administrative_area)

    cluster_resp = await client.post(
        "/api/v1/clusters",
        json={"title": f"Water quality issues {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(validator_user),
    )
    cluster_id = cluster_resp.json()["id"]

    await client.patch(
        f"/api/v1/challenges/{challenge_id}",
        json={"cluster_id": cluster_id},
        headers=auth_headers(validator_user),
    )

    project_resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"Water Quality Project {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    assert project_resp.status_code == 201
    assert project_resp.json()["organization_id"] == str(university_org.id)

    list_resp = await client.get("/api/v1/projects", headers=auth_headers(coordinator_user))
    assert project_resp.json()["id"] in {p["id"] for p in list_resp.json()["items"]}


@pytest.mark.asyncio
async def test_only_validator_or_superadmin_can_cluster_a_challenge(
    client, citizen_user, field_assistant_user, administrative_area, validator_user
):
    challenge_id = await _submit_challenge(client, citizen_user, administrative_area)
    cluster_resp = await client.post(
        "/api/v1/clusters",
        json={"title": f"Unauthorized clustering attempt {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(validator_user),
    )
    cluster_id = cluster_resp.json()["id"]

    # A citizen (the submitter) cannot cluster their own challenge.
    resp = await client.patch(
        f"/api/v1/challenges/{challenge_id}",
        json={"cluster_id": cluster_id},
        headers=auth_headers(citizen_user),
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "FORBIDDEN"

    # Nor can a field assistant.
    resp = await client.patch(
        f"/api/v1/challenges/{challenge_id}",
        json={"cluster_id": cluster_id},
        headers=auth_headers(field_assistant_user),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_university_opportunities_excludes_clusters_already_claimed_by_a_project(
    client, citizen_user, validator_user, coordinator_user, administrative_area
):
    """Regression for the University Opportunities page showing stale
    already-claimed clusters (e.g. leftover E2E test clusters that already
    have a project) - GET /clusters?unclaimed=true must exclude any cluster
    with an existing Project, matching the same has-project exclusion
    ClusterRepository.find_open_nearest_by_embedding already uses."""
    challenge_id = await _submit_challenge(client, citizen_user, administrative_area)

    unclaimed_cluster_resp = await client.post(
        "/api/v1/clusters",
        json={"title": f"Unclaimed opportunity {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(validator_user),
    )
    unclaimed_cluster_id = unclaimed_cluster_resp.json()["id"]

    claimed_cluster_resp = await client.post(
        "/api/v1/clusters",
        json={"title": f"Already claimed cluster {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(validator_user),
    )
    claimed_cluster_id = claimed_cluster_resp.json()["id"]

    await client.patch(
        f"/api/v1/challenges/{challenge_id}",
        json={"cluster_id": claimed_cluster_id},
        headers=auth_headers(validator_user),
    )
    project_resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": claimed_cluster_id, "title": f"Claiming Project {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    assert project_resp.status_code == 201

    resp = await client.get("/api/v1/clusters", params={"status": "active", "unclaimed": "true", "limit": 100})
    assert resp.status_code == 200
    ids = {c["id"] for c in resp.json()["items"]}
    assert unclaimed_cluster_id in ids
    assert claimed_cluster_id not in ids

    # The plain (unfiltered) listing still shows both - Validators managing
    # all clusters must not lose visibility of already-claimed ones.
    all_resp = await client.get("/api/v1/clusters", params={"status": "active", "limit": 100})
    all_ids = {c["id"] for c in all_resp.json()["items"]}
    assert unclaimed_cluster_id in all_ids
    assert claimed_cluster_id in all_ids


@pytest.mark.asyncio
async def test_clustering_with_a_nonexistent_cluster_id_is_rejected(
    client, citizen_user, validator_user, administrative_area
):
    challenge_id = await _submit_challenge(client, citizen_user, administrative_area)
    resp = await client.patch(
        f"/api/v1/challenges/{challenge_id}",
        json={"cluster_id": str(uuid.uuid4())},
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 422
    assert resp.json()["code"] == "INVALID_CLUSTER"
