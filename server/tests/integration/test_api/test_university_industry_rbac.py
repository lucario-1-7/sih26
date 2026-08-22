import uuid

import pytest

from tests.conftest import auth_headers


async def _make_cluster(client, validator_user) -> str:
    resp = await client.post(
        "/api/v1/clusters",
        json={"title": f"Univ/Industry RBAC Test Cluster {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_coordinator_can_create_a_project_scoped_to_their_own_organization(
    client, validator_user, coordinator_user, university_org
):
    cluster_id = await _make_cluster(client, validator_user)
    resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"Coordinator Project {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    assert resp.status_code == 201
    assert resp.json()["organization_id"] == str(university_org.id)


@pytest.mark.asyncio
async def test_faculty_can_update_project_status(client, validator_user, coordinator_user, faculty_user):
    cluster_id = await _make_cluster(client, validator_user)
    create_resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"Faculty Update Project {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    project_id = create_resp.json()["id"]

    # New lifecycle: proposed -> accepted -> active (no skipping states).
    resp = await client.patch(
        f"/api/v1/projects/{project_id}",
        json={"status": "accepted"},
        headers=auth_headers(faculty_user),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"

    resp = await client.patch(
        f"/api/v1/projects/{project_id}",
        json={"status": "active"},
        headers=auth_headers(faculty_user),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "active"


@pytest.mark.asyncio
async def test_faculty_cannot_manage_another_universitys_project(client, db, validator_user, coordinator_user):
    from app.models.enums import Domain, OrganizationType, Role
    from app.models.organization import Organization
    from app.models.user import User

    other_org = Organization(
        name=f"Other University B {uuid.uuid4().hex[:8]}", type=OrganizationType.UNIVERSITY, domain_tags=[]
    )
    db.add(other_org)
    await db.commit()
    await db.refresh(other_org)

    other_faculty = User(
        phone=f"+91{uuid.uuid4().int % 10**10:010d}",
        name="Faculty B",
        role=Role.FACULTY,
        domain=Domain.UNIVERSITY,
        organization_id=other_org.id,
    )
    db.add(other_faculty)
    await db.commit()
    await db.refresh(other_faculty)

    cluster_id = await _make_cluster(client, validator_user)
    create_resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"University A Project {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    project_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/projects/{project_id}",
        json={"status": "accepted"},
        headers=auth_headers(other_faculty),
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_faculty_can_submit_a_solution_for_own_project(client, validator_user, coordinator_user, faculty_user):
    cluster_id = await _make_cluster(client, validator_user)
    create_resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"Faculty Solution Project {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    project_id = create_resp.json()["id"]

    resp = await client.post(
        "/api/v1/solutions",
        json={"project_id": project_id, "title": "Deployed low-cost water filtration prototype"},
        headers=auth_headers(faculty_user),
    )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_industry_is_an_authenticated_role_but_cannot_manage_validation_or_users(
    client, industry_user
):
    resp = await client.get("/api/v1/users/me", headers=auth_headers(industry_user))
    assert resp.status_code == 200
    assert resp.json()["role"] == "industry"

    resp = await client.post(
        "/api/v1/duplicate/decisions",
        json={
            "challenge_id": str(uuid.uuid4()),
            "candidate_challenge_id": str(uuid.uuid4()),
            "decision": "duplicate",
        },
        headers=auth_headers(industry_user),
    )
    assert resp.status_code == 403

    resp = await client.post(
        "/api/v1/users",
        json={"phone": "+919000000222", "name": "x", "role": "industry", "domain": "industry"},
        headers=auth_headers(industry_user),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_industry_cannot_register_organizations_only_superadmin_can(client, industry_user):
    resp = await client.post(
        "/api/v1/matching/organizations",
        json={"name": f"Rogue Org {uuid.uuid4().hex[:8]}", "type": "industry", "domain_tags": []},
        headers=auth_headers(industry_user),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_coordinator_cannot_create_cluster_or_theme(client, coordinator_user):
    resp = await client.post(
        "/api/v1/clusters",
        json={"title": f"Coordinator Should Not Create {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    assert resp.status_code == 403
