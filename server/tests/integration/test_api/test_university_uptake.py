"""Regression coverage for "which university has taken up this project" -
Project.organization_id (existing FK, set at create_project time) combined
with the existing PROJECT_STATUS_TRANSITIONS accept step. See
project_service.to_response / _has_been_taken_up.

No new database relationship was introduced - this exercises the existing
Challenge -> Cluster -> Project pipeline plus the existing project status
state machine (PROPOSED -> ACCEPTED -> ACTIVE), and the new `university`
field the API response now derives from it.
"""

import uuid

import pytest

from app.models.enums import Domain, OrganizationType, Role
from app.models.organization import Organization
from app.models.user import User
from tests.conftest import auth_headers


async def _make_cluster(client, validator_user) -> str:
    resp = await client.post(
        "/api/v1/clusters",
        json={"title": f"Uptake Test Cluster {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_proposed_project_reports_no_university(client, validator_user, coordinator_user):
    """A project that has only been proposed (created) must not report a
    university - creation alone is not uptake."""
    cluster_id = await _make_cluster(client, validator_user)
    resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"Not Yet Accepted {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "proposed"
    assert body["university"] is None


@pytest.mark.asyncio
async def test_accepting_the_project_establishes_the_university_relationship(
    client, validator_user, coordinator_user, university_org
):
    cluster_id = await _make_cluster(client, validator_user)
    create_resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"Accept Me {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    project_id = create_resp.json()["id"]
    assert create_resp.json()["university"] is None

    accept_resp = await client.patch(
        f"/api/v1/projects/{project_id}", json={"status": "accepted"}, headers=auth_headers(coordinator_user)
    )
    assert accept_resp.status_code == 200
    body = accept_resp.json()
    assert body["status"] == "accepted"
    assert body["university"] == {
        "id": str(university_org.id),
        "name": university_org.name,
        "type": "university",
    }


@pytest.mark.asyncio
async def test_rejected_proposal_never_establishes_a_false_uptake(client, validator_user, coordinator_user):
    """CANCELLED reached directly from PROPOSED (a rejected proposal that
    was never accepted) must not report a university."""
    cluster_id = await _make_cluster(client, validator_user)
    create_resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"Reject Me {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    project_id = create_resp.json()["id"]

    cancel_resp = await client.patch(
        f"/api/v1/projects/{project_id}", json={"status": "cancelled"}, headers=auth_headers(coordinator_user)
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"
    assert cancel_resp.json()["university"] is None


@pytest.mark.asyncio
async def test_invalid_lifecycle_transition_cannot_establish_uptake(client, validator_user, coordinator_user):
    """PROPOSED -> ACTIVE is not a legal transition (must go through
    ACCEPTED first) - the attempt must be rejected and no uptake recorded."""
    cluster_id = await _make_cluster(client, validator_user)
    create_resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"Skip Accept {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    project_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/projects/{project_id}", json={"status": "active"}, headers=auth_headers(coordinator_user)
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == "INVALID_STATUS_TRANSITION"

    get_resp = await client.get(f"/api/v1/projects/{project_id}")
    assert get_resp.json()["status"] == "proposed"
    assert get_resp.json()["university"] is None


@pytest.mark.asyncio
async def test_a_different_university_cannot_accept_another_universitys_project(
    client, db, validator_user, coordinator_user
):
    """Cross-organization isolation: University B's coordinator cannot
    accept (and thereby cannot fabricate an uptake relationship for)
    University A's project."""
    other_org = Organization(
        name=f"Other University {uuid.uuid4().hex[:8]}", type=OrganizationType.UNIVERSITY, domain_tags=[]
    )
    db.add(other_org)
    await db.commit()
    await db.refresh(other_org)
    other_coordinator = User(
        phone=f"+919{uuid.uuid4().int % 10**9:09d}",
        name="Other Coordinator",
        role=Role.COORDINATOR,
        domain=Domain.UNIVERSITY,
        organization_id=other_org.id,
    )
    db.add(other_coordinator)
    await db.commit()
    await db.refresh(other_coordinator)

    cluster_id = await _make_cluster(client, validator_user)
    create_resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"University A's Project {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    project_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/projects/{project_id}", json={"status": "accepted"}, headers=auth_headers(other_coordinator)
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "FORBIDDEN"

    get_resp = await client.get(f"/api/v1/projects/{project_id}")
    assert get_resp.json()["university"] is None


@pytest.mark.asyncio
async def test_multiple_roles_see_the_same_university_for_the_same_project(
    client, validator_user, coordinator_user, faculty_user, industry_user, superadmin_user
):
    """The uptake field is read through the same open GET/list convention
    challenges/clusters already use - every role (and an unauthenticated
    caller) sees the identical real university for the identical project."""
    cluster_id = await _make_cluster(client, validator_user)
    create_resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"Widely Visible {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    project_id = create_resp.json()["id"]
    await client.patch(
        f"/api/v1/projects/{project_id}", json={"status": "accepted"}, headers=auth_headers(coordinator_user)
    )

    expected = (await client.get(f"/api/v1/projects/{project_id}")).json()["university"]
    assert expected is not None

    for user in (validator_user, coordinator_user, faculty_user, industry_user, superadmin_user, None):
        headers = auth_headers(user) if user is not None else {}
        resp = await client.get(f"/api/v1/projects/{project_id}", headers=headers)
        assert resp.json()["university"] == expected


@pytest.mark.asyncio
async def test_uptake_persists_across_a_fresh_request_and_appears_in_list(
    client, validator_user, coordinator_user, university_org
):
    cluster_id = await _make_cluster(client, validator_user)
    create_resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"Persisted Uptake {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    project_id = create_resp.json()["id"]
    await client.patch(
        f"/api/v1/projects/{project_id}", json={"status": "accepted"}, headers=auth_headers(coordinator_user)
    )

    # A fresh, independent GET (simulating a page refresh / a different client).
    get_resp = await client.get(f"/api/v1/projects/{project_id}")
    assert get_resp.json()["university"]["id"] == str(university_org.id)

    # And it shows up correctly in the list endpoint too, not just the detail one.
    list_resp = await client.get("/api/v1/projects", params={"cluster_id": cluster_id})
    items = list_resp.json()["items"]
    assert any(p["id"] == project_id and p["university"]["id"] == str(university_org.id) for p in items)
