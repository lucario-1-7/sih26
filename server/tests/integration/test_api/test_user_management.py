import uuid

import pytest

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_superadmin_can_create_a_government_validator(client, superadmin_user):
    phone = f"+9199{uuid.uuid4().int % 10**8:08d}"
    resp = await client.post(
        "/api/v1/users",
        json={"phone": phone, "name": "New Validator", "role": "validator", "domain": "government"},
        headers=auth_headers(superadmin_user),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["role"] == "validator"
    assert body["domain"] == "government"
    assert body["is_active"] is True


@pytest.mark.asyncio
async def test_superadmin_can_create_a_university_coordinator_with_organization(
    client, superadmin_user, university_org
):
    phone = f"+9198{uuid.uuid4().int % 10**8:08d}"
    resp = await client.post(
        "/api/v1/users",
        json={
            "phone": phone,
            "name": "New Coordinator",
            "role": "coordinator",
            "domain": "university",
            "organization_id": str(university_org.id),
        },
        headers=auth_headers(superadmin_user),
    )
    assert resp.status_code == 201
    assert resp.json()["organization_id"] == str(university_org.id)


@pytest.mark.asyncio
async def test_university_domain_requires_an_organization(client, superadmin_user):
    phone = f"+9197{uuid.uuid4().int % 10**8:08d}"
    resp = await client.post(
        "/api/v1/users",
        json={"phone": phone, "name": "No Org Coordinator", "role": "coordinator", "domain": "university"},
        headers=auth_headers(superadmin_user),
    )
    assert resp.status_code == 422
    assert resp.json()["code"] == "ORGANIZATION_REQUIRED"


@pytest.mark.asyncio
async def test_cannot_create_invalid_domain_role_combination(client, superadmin_user, university_org):
    phone = f"+9196{uuid.uuid4().int % 10**8:08d}"
    resp = await client.post(
        "/api/v1/users",
        json={
            "phone": phone,
            "name": "Invalid Combo",
            "role": "validator",
            "domain": "university",
            "organization_id": str(university_org.id),
        },
        headers=auth_headers(superadmin_user),
    )
    assert resp.status_code == 422
    assert resp.json()["code"] == "INVALID_DOMAIN_ROLE"


@pytest.mark.asyncio
async def test_non_superadmin_cannot_create_users(client, validator_user):
    phone = f"+9195{uuid.uuid4().int % 10**8:08d}"
    resp = await client.post(
        "/api/v1/users",
        json={"phone": phone, "name": "Sneaky", "role": "validator", "domain": "government"},
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_superadmin_can_deactivate_a_user(client, superadmin_user, field_assistant_user):
    resp = await client.patch(
        f"/api/v1/users/{field_assistant_user.id}",
        json={"is_active": False},
        headers=auth_headers(superadmin_user),
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_superadmin_can_reassign_role_domain_and_organization(
    client, superadmin_user, field_assistant_user, university_org
):
    resp = await client.patch(
        f"/api/v1/users/{field_assistant_user.id}",
        json={"role": "coordinator", "domain": "university", "organization_id": str(university_org.id)},
        headers=auth_headers(superadmin_user),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "coordinator"
    assert body["domain"] == "university"
    assert body["organization_id"] == str(university_org.id)


@pytest.mark.asyncio
async def test_superadmin_cannot_change_their_own_role(client, superadmin_user):
    resp = await client.patch(
        f"/api/v1/users/{superadmin_user.id}",
        json={"role": "citizen", "domain": "citizen"},
        headers=auth_headers(superadmin_user),
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "SELF_MODIFICATION_FORBIDDEN"


@pytest.mark.asyncio
async def test_user_cannot_change_their_own_organization(client, coordinator_user, industry_org):
    resp = await client.patch(
        f"/api/v1/users/{coordinator_user.id}",
        json={"organization_id": str(industry_org.id)},
        headers=auth_headers(coordinator_user),
    )
    # A non-superadmin gets 403 from the role dependency before the
    # self-modification check is ever reached — either way, it's forbidden.
    assert resp.status_code == 403
