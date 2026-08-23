"""Strict input validation on POST /challenges. Backend is authoritative
regardless of what the frontend already blocks. Every case here must be
rejected before it ever reaches persistence."""

import uuid

import pytest

from tests.conftest import auth_headers

VALID_TITLE = "Broken streetlight on Main Road"
VALID_DESCRIPTION = "The streetlight outside the community hall has been dark for two weeks now."


async def _post_challenge(client, citizen_user, **overrides):
    body = {
        "title": VALID_TITLE,
        "description": VALID_DESCRIPTION,
        "administrative_area_id": overrides.pop("administrative_area_id", str(uuid.uuid4())),
        **overrides,
    }
    return await client.post("/api/v1/challenges", json=body, headers=auth_headers(citizen_user))


@pytest.mark.asyncio
async def test_empty_title_is_rejected(client, citizen_user, administrative_area):
    resp = await _post_challenge(
        client, citizen_user, title="", administrative_area_id=str(administrative_area.id)
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_whitespace_only_title_is_rejected(client, citizen_user, administrative_area):
    resp = await _post_challenge(
        client, citizen_user, title="     ", administrative_area_id=str(administrative_area.id)
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_too_short_description_is_rejected(client, citizen_user, administrative_area):
    resp = await _post_challenge(
        client, citizen_user, description="too short", administrative_area_id=str(administrative_area.id)
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_missing_title_is_rejected(client, citizen_user, administrative_area):
    body = {"description": VALID_DESCRIPTION, "administrative_area_id": str(administrative_area.id)}
    resp = await client.post("/api/v1/challenges", json=body, headers=auth_headers(citizen_user))
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_administrative_area_id_must_be_a_valid_uuid(client, citizen_user):
    resp = await _post_challenge(client, citizen_user, administrative_area_id="not-a-uuid")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_administrative_area_id_must_reference_an_existing_row(client, citizen_user):
    resp = await _post_challenge(client, citizen_user, administrative_area_id=str(uuid.uuid4()))
    assert resp.status_code == 422
    assert resp.json()["code"] == "INVALID_ADMINISTRATIVE_AREA"


@pytest.mark.asyncio
async def test_extra_unexpected_fields_are_rejected(client, citizen_user, administrative_area):
    resp = await _post_challenge(
        client,
        citizen_user,
        administrative_area_id=str(administrative_area.id),
        status="resolved",  # a client must never be able to set this directly
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_field_assistant_and_citizen_only_others_are_forbidden(
    client, validator_user, industry_user, administrative_area
):
    for user in (validator_user, industry_user):
        resp = await _post_challenge(client, user, administrative_area_id=str(administrative_area.id))
        assert resp.status_code == 403, user.role


@pytest.mark.asyncio
async def test_title_over_max_length_is_rejected(client, citizen_user, administrative_area):
    resp = await _post_challenge(
        client, citizen_user, title="x" * 201, administrative_area_id=str(administrative_area.id)
    )
    assert resp.status_code == 422
