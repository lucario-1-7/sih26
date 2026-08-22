import uuid

import pytest

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_field_assistant_can_create_an_assisted_submission(client, administrative_area, field_assistant_user):
    resp = await client.post(
        "/api/v1/challenges",
        json={
            "title": "Broken handpump in village square",
            "description": "The village handpump has been broken for over a week, no clean water access.",
            "administrative_area_id": str(administrative_area.id),
        },
        headers=auth_headers(field_assistant_user),
    )
    assert resp.status_code == 201
    assert resp.json()["submitted_by_id"] == str(field_assistant_user.id)


@pytest.mark.asyncio
async def test_field_assistant_can_store_on_behalf_of_information(
    client, administrative_area, field_assistant_user
):
    resp = await client.post(
        "/api/v1/challenges",
        json={
            "title": "Blocked drainage near primary school",
            "description": "The drainage channel near the primary school has been blocked for two weeks now.",
            "administrative_area_id": str(administrative_area.id),
            "on_behalf_of_name": "Ramesh Kumar",
            "on_behalf_of_phone": "+919812345678",
        },
        headers=auth_headers(field_assistant_user),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["on_behalf_of_name"] == "Ramesh Kumar"
    assert body["on_behalf_of_phone"] == "+919812345678"


@pytest.mark.asyncio
async def test_citizen_on_behalf_of_fields_are_ignored(client, administrative_area, citizen_user):
    """A citizen submitting their own challenge has no one to submit "on
    behalf of" — the field is silently dropped, not stored, even if sent."""
    resp = await client.post(
        "/api/v1/challenges",
        json={
            "title": "Citizen self-submission with spoofed on-behalf-of",
            "description": "Testing that on_behalf_of fields are ignored for citizen self-submissions.",
            "administrative_area_id": str(administrative_area.id),
            "on_behalf_of_name": "Should Be Ignored",
        },
        headers=auth_headers(citizen_user),
    )
    assert resp.status_code == 201
    assert resp.json()["on_behalf_of_name"] is None


@pytest.mark.asyncio
async def test_field_assistant_cannot_make_a_duplicate_decision(
    client, db, administrative_area, citizen_user, field_assistant_user
):
    from app.models.challenge import Challenge
    from app.repositories.duplicate_repository import DuplicateRepository

    original = Challenge(
        title="Overflowing drain near school",
        description="The drain near the government school has been overflowing for several days now.",
        submitted_by_id=citizen_user.id,
        administrative_area_id=administrative_area.id,
    )
    dup = Challenge(
        title="Drain overflow close to school",
        description="Drainage near the school is overflowing badly, has been like this for days.",
        submitted_by_id=citizen_user.id,
        administrative_area_id=administrative_area.id,
    )
    db.add_all([original, dup])
    await db.commit()
    await db.refresh(original)
    await db.refresh(dup)
    await DuplicateRepository(db).create_candidate(
        challenge_id=dup.id,
        candidate_challenge_id=original.id,
        similarity_score=0.9,
        model_name="paraphrase-multilingual-MiniLM-L12-v2",
        model_version="1",
    )
    await db.commit()

    resp = await client.post(
        "/api/v1/duplicate/decisions",
        json={"challenge_id": str(dup.id), "candidate_challenge_id": str(original.id), "decision": "duplicate"},
        headers=auth_headers(field_assistant_user),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_field_assistant_cannot_access_validator_only_candidate_queue(
    client, administrative_area, citizen_user, field_assistant_user
):
    resp = await client.get(
        f"/api/v1/duplicate/challenges/{uuid.uuid4()}/candidates",
        headers=auth_headers(field_assistant_user),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_validator_cannot_call_superadmin_user_management(client, validator_user):
    resp = await client.post(
        "/api/v1/users",
        json={"phone": "+919000000111", "name": "x", "role": "validator", "domain": "government"},
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_validator_can_set_challenge_severity_but_citizen_cannot(
    client, administrative_area, citizen_user, validator_user
):
    create_resp = await client.post(
        "/api/v1/challenges",
        json={
            "title": "Collapsed culvert on approach road",
            "description": "The culvert on the approach road to the village has collapsed after heavy rain.",
            "administrative_area_id": str(administrative_area.id),
        },
        headers=auth_headers(citizen_user),
    )
    challenge_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/challenges/{challenge_id}",
        json={"severity": "high"},
        headers=auth_headers(citizen_user),
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "FORBIDDEN"

    resp = await client.patch(
        f"/api/v1/challenges/{challenge_id}",
        json={"severity": "high"},
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 200
    assert resp.json()["severity"] == "high"


@pytest.mark.asyncio
async def test_citizen_cannot_edit_another_citizens_challenge(
    client, db, administrative_area, citizen_user
):
    from app.models.enums import Domain, Role
    from app.models.user import User

    other_citizen = User(
        phone=f"+91{uuid.uuid4().int % 10**10:010d}", name="Other Citizen", role=Role.CITIZEN, domain=Domain.CITIZEN
    )
    db.add(other_citizen)
    await db.commit()
    await db.refresh(other_citizen)

    create_resp = await client.post(
        "/api/v1/challenges",
        json={
            "title": "Streetlight outage on main lane",
            "description": "Streetlight on the main lane has stopped working, area is dark at night.",
            "administrative_area_id": str(administrative_area.id),
        },
        headers=auth_headers(citizen_user),
    )
    challenge_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/challenges/{challenge_id}",
        json={"title": "Hijacked title"},
        headers=auth_headers(other_citizen),
    )
    assert resp.status_code == 403
