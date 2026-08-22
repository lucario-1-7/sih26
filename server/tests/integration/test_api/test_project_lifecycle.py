import uuid

import pytest

from tests.conftest import auth_headers


async def _make_cluster(client, validator_user) -> str:
    resp = await client.post(
        "/api/v1/clusters",
        json={"title": f"Lifecycle Test Cluster {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _make_project(client, coordinator_user, cluster_id: str) -> dict:
    resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"Lifecycle Test Project {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_project_starts_proposed(client, validator_user, coordinator_user):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)
    assert project["status"] == "proposed"


@pytest.mark.asyncio
async def test_valid_full_lifecycle_transition(client, validator_user, coordinator_user):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)
    pid = project["id"]

    for target in ("accepted", "active", "on_hold", "active", "completed"):
        resp = await client.patch(
            f"/api/v1/projects/{pid}", json={"status": target}, headers=auth_headers(coordinator_user)
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == target


@pytest.mark.asyncio
async def test_cannot_skip_states(client, validator_user, coordinator_user):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)
    pid = project["id"]

    resp = await client.patch(
        f"/api/v1/projects/{pid}", json={"status": "active"}, headers=auth_headers(coordinator_user)
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == "INVALID_STATUS_TRANSITION"


@pytest.mark.asyncio
async def test_cannot_transition_out_of_completed(client, validator_user, coordinator_user):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)
    pid = project["id"]

    for target in ("accepted", "active", "completed"):
        await client.patch(f"/api/v1/projects/{pid}", json={"status": target}, headers=auth_headers(coordinator_user))

    resp = await client.patch(
        f"/api/v1/projects/{pid}", json={"status": "active"}, headers=auth_headers(coordinator_user)
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_cancel_is_reachable_from_proposed(client, validator_user, coordinator_user):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)
    pid = project["id"]

    resp = await client.patch(
        f"/api/v1/projects/{pid}", json={"status": "cancelled"}, headers=auth_headers(coordinator_user)
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_milestone_create_update_complete(client, validator_user, coordinator_user, faculty_user):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)
    pid = project["id"]

    resp = await client.post(
        f"/api/v1/projects/{pid}/milestones",
        json={"title": "Site survey completed", "order": 1},
        headers=auth_headers(faculty_user),
    )
    assert resp.status_code == 201
    milestone = resp.json()
    assert milestone["status"] == "pending"
    assert milestone["completed_at"] is None

    resp = await client.patch(
        f"/api/v1/projects/{pid}/milestones/{milestone['id']}",
        json={"status": "completed"},
        headers=auth_headers(faculty_user),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    assert body["completed_at"] is not None


@pytest.mark.asyncio
async def test_milestone_authorization_cross_institution(client, db, validator_user, coordinator_user):
    from app.models.enums import Domain, OrganizationType, Role
    from app.models.organization import Organization
    from app.models.user import User

    other_org = Organization(
        name=f"Other Milestone Org {uuid.uuid4().hex[:8]}", type=OrganizationType.UNIVERSITY, domain_tags=[]
    )
    db.add(other_org)
    await db.commit()
    await db.refresh(other_org)
    other_faculty = User(
        phone=f"+91{uuid.uuid4().int % 10**10:010d}",
        name="Other Milestone Faculty",
        role=Role.FACULTY,
        domain=Domain.UNIVERSITY,
        organization_id=other_org.id,
    )
    db.add(other_faculty)
    await db.commit()
    await db.refresh(other_faculty)

    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)

    resp = await client.post(
        f"/api/v1/projects/{project['id']}/milestones",
        json={"title": "Should not be allowed"},
        headers=auth_headers(other_faculty),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_deliverable_submit_and_verify(client, validator_user, coordinator_user, faculty_user):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)
    pid = project["id"]

    resp = await client.post(
        f"/api/v1/projects/{pid}/deliverables",
        json={"title": "Final report"},
        headers=auth_headers(faculty_user),
    )
    deliverable_id = resp.json()["id"]
    assert resp.json()["status"] == "pending"

    resp = await client.patch(
        f"/api/v1/projects/{pid}/deliverables/{deliverable_id}",
        json={"evidence": "https://example.org/report.pdf"},
        headers=auth_headers(faculty_user),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "submitted"

    # Faculty cannot verify their own submission.
    resp = await client.post(
        f"/api/v1/projects/{pid}/deliverables/{deliverable_id}/verify",
        json={"approve": True},
        headers=auth_headers(faculty_user),
    )
    assert resp.status_code == 403

    resp = await client.post(
        f"/api/v1/projects/{pid}/deliverables/{deliverable_id}/verify",
        json={"approve": True},
        headers=auth_headers(coordinator_user),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "verified"
    assert body["verified_by_id"] == str(coordinator_user.id)
