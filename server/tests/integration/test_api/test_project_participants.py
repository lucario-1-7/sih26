import uuid

import pytest

from tests.conftest import auth_headers


async def _make_cluster(client, validator_user) -> str:
    resp = await client.post(
        "/api/v1/clusters",
        json={"title": f"Participant Test Cluster {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _make_project(client, coordinator_user, cluster_id: str) -> dict:
    resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"Participant Test Project {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_faculty_can_create_a_student_participant_record(
    client, validator_user, coordinator_user, faculty_user
):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)

    resp = await client.post(
        f"/api/v1/projects/{project['id']}/participants",
        json={"name": "Asha Verma", "department": "Civil Engineering", "academic_year": "3"},
        headers=auth_headers(faculty_user),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Asha Verma"
    assert body["project_id"] == project["id"]
    assert body["is_active"] is True


@pytest.mark.asyncio
async def test_faculty_can_update_a_student_participant_record(
    client, validator_user, coordinator_user, faculty_user
):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)

    create_resp = await client.post(
        f"/api/v1/projects/{project['id']}/participants",
        json={"name": "Rohit Singh"},
        headers=auth_headers(faculty_user),
    )
    participant_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/projects/{project['id']}/participants/{participant_id}",
        json={"academic_year": "4", "is_active": False},
        headers=auth_headers(faculty_user),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["academic_year"] == "4"
    assert body["is_active"] is False


@pytest.mark.asyncio
async def test_coordinator_can_manage_participants_of_own_institution_project(
    client, validator_user, coordinator_user
):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)

    resp = await client.post(
        f"/api/v1/projects/{project['id']}/participants",
        json={"name": "Priya Nair"},
        headers=auth_headers(coordinator_user),
    )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_faculty_from_another_university_cannot_manage_participants(
    client, db, validator_user, coordinator_user, faculty_user
):
    """Faculty A (university B) must not manage University A's project participants."""
    from app.models.enums import Domain, OrganizationType, Role
    from app.models.organization import Organization
    from app.models.user import User

    other_org = Organization(
        name=f"Other University {uuid.uuid4().hex[:8]}", type=OrganizationType.UNIVERSITY, domain_tags=[]
    )
    db.add(other_org)
    await db.commit()
    await db.refresh(other_org)

    other_faculty = User(
        phone=f"+91{uuid.uuid4().int % 10**10:010d}",
        name="Other Faculty",
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
        f"/api/v1/projects/{project['id']}/participants",
        json={"name": "Should Not Be Created"},
        headers=auth_headers(other_faculty),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_no_student_login_route_or_role_exists(client):
    from app.models.enums import Role

    assert not any(r.value == "student" for r in Role)
    # There is no student-facing OTP/login flow distinct from citizen — the
    # only authentication surface is /auth/otp/*, shared by all roles, and no
    # role named "student" can ever appear in a JWT.
    resp = await client.post("/api/v1/auth/otp/request", json={"phone": "+919000000000"})
    assert resp.status_code == 202
