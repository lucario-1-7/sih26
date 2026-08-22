import uuid

import pytest

from tests.conftest import auth_headers


async def _make_cluster(client, validator_user) -> str:
    resp = await client.post(
        "/api/v1/clusters",
        json={"title": f"Collab Test Cluster {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _make_project(client, coordinator_user, cluster_id: str) -> dict:
    resp = await client.post(
        "/api/v1/projects",
        json={"cluster_id": cluster_id, "title": f"Collab Test Project {uuid.uuid4().hex[:8]}"},
        headers=auth_headers(coordinator_user),
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_industry_can_express_interest(client, validator_user, coordinator_user, industry_user):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)

    resp = await client.post(
        "/api/v1/collaborations",
        json={"project_id": project["id"], "type": "funding"},
        headers=auth_headers(industry_user),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "interested"
    assert body["organization_id"] == str(industry_user.organization_id)


@pytest.mark.asyncio
async def test_full_collaboration_lifecycle(client, validator_user, coordinator_user, industry_user):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)

    resp = await client.post(
        "/api/v1/collaborations",
        json={"project_id": project["id"], "type": "mentoring"},
        headers=auth_headers(industry_user),
    )
    collab_id = resp.json()["id"]

    # Industry formalizes interest into a proposal.
    resp = await client.patch(
        f"/api/v1/collaborations/{collab_id}/status",
        json={"status": "proposed", "proposal": "We can provide senior engineer mentoring."},
        headers=auth_headers(industry_user),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "proposed"

    # University/gov cannot act on behalf of industry to propose again, but
    # university accepts.
    resp = await client.patch(
        f"/api/v1/collaborations/{collab_id}/status",
        json={"status": "accepted"},
        headers=auth_headers(coordinator_user),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"

    resp = await client.patch(
        f"/api/v1/collaborations/{collab_id}/status",
        json={"status": "active"},
        headers=auth_headers(coordinator_user),
    )
    assert resp.status_code == 200

    resp = await client.patch(
        f"/api/v1/collaborations/{collab_id}/status",
        json={"status": "completed"},
        headers=auth_headers(coordinator_user),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_industry_cannot_accept_its_own_proposal(client, validator_user, coordinator_user, industry_user):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)

    resp = await client.post(
        "/api/v1/collaborations",
        json={"project_id": project["id"], "type": "equipment"},
        headers=auth_headers(industry_user),
    )
    collab_id = resp.json()["id"]
    await client.patch(
        f"/api/v1/collaborations/{collab_id}/status",
        json={"status": "proposed"},
        headers=auth_headers(industry_user),
    )

    resp = await client.patch(
        f"/api/v1/collaborations/{collab_id}/status",
        json={"status": "accepted"},
        headers=auth_headers(industry_user),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_industry_can_propose_a_funding_commitment_and_university_reviews_it(
    client, validator_user, coordinator_user, industry_user
):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)

    resp = await client.post(
        "/api/v1/collaborations",
        json={"project_id": project["id"], "type": "funding"},
        headers=auth_headers(industry_user),
    )
    collab_id = resp.json()["id"]

    resp = await client.post(
        f"/api/v1/collaborations/{collab_id}/commitments",
        json={"type": "funding", "amount": 50000, "currency": "INR", "description": "Pilot funding"},
        headers=auth_headers(industry_user),
    )
    assert resp.status_code == 201
    commitment = resp.json()
    assert commitment["status"] == "proposed"

    # Industry cannot self-approve its own commitment.
    resp = await client.patch(
        f"/api/v1/collaborations/{collab_id}/commitments/{commitment['id']}/status",
        json={"status": "accepted"},
        headers=auth_headers(industry_user),
    )
    assert resp.status_code == 403

    resp = await client.patch(
        f"/api/v1/collaborations/{collab_id}/commitments/{commitment['id']}/status",
        json={"status": "accepted"},
        headers=auth_headers(coordinator_user),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_industry_cannot_access_another_industrys_collaboration_commitments_review(
    client, db, validator_user, coordinator_user, industry_user
):
    """Industry A must not be able to review/accept its own or another
    company's commitments — that authority belongs only to the university."""
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)

    resp = await client.post(
        "/api/v1/collaborations",
        json={"project_id": project["id"], "type": "technical_support"},
        headers=auth_headers(industry_user),
    )
    collab_id = resp.json()["id"]

    from app.models.enums import Domain, OrganizationType, Role
    from app.models.organization import Organization
    from app.models.user import User

    other_org = Organization(
        name=f"Other Industry {uuid.uuid4().hex[:8]}", type=OrganizationType.INDUSTRY, domain_tags=[]
    )
    db.add(other_org)
    await db.commit()
    await db.refresh(other_org)
    other_industry = User(
        phone=f"+91{uuid.uuid4().int % 10**10:010d}",
        name="Other Industry User",
        role=Role.INDUSTRY,
        domain=Domain.INDUSTRY,
        organization_id=other_org.id,
    )
    db.add(other_industry)
    await db.commit()
    await db.refresh(other_industry)

    resp = await client.post(
        f"/api/v1/collaborations/{collab_id}/commitments",
        json={"type": "equipment", "description": "Rogue commitment"},
        headers=auth_headers(other_industry),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_unauthorized_role_cannot_create_collaboration(client, validator_user, coordinator_user):
    cluster_id = await _make_cluster(client, validator_user)
    project = await _make_project(client, coordinator_user, cluster_id)

    resp = await client.post(
        "/api/v1/collaborations",
        json={"project_id": project["id"], "type": "funding"},
        headers=auth_headers(coordinator_user),
    )
    assert resp.status_code == 403
