import uuid

import pytest

from app.models.administrative_area import AdministrativeArea
from app.models.enums import AdministrativeLevel


@pytest.mark.asyncio
async def test_list_administrative_areas_returns_real_rows(client, db):
    state = AdministrativeArea(name=f"Test State {uuid.uuid4().hex[:8]}", level=AdministrativeLevel.STATE)
    db.add(state)
    await db.commit()
    await db.refresh(state)
    district = AdministrativeArea(
        name=f"Test District {uuid.uuid4().hex[:8]}", level=AdministrativeLevel.DISTRICT, parent_id=state.id
    )
    db.add(district)
    await db.commit()
    await db.refresh(district)

    resp = await client.get("/api/v1/administrative-areas")
    assert resp.status_code == 200
    body = resp.json()
    ids = {item["id"] for item in body["items"]}
    assert str(state.id) in ids
    assert str(district.id) in ids


@pytest.mark.asyncio
async def test_list_administrative_areas_filters_by_level(client, db):
    village = AdministrativeArea(name=f"Test Village {uuid.uuid4().hex[:8]}", level=AdministrativeLevel.VILLAGE)
    db.add(village)
    await db.commit()
    await db.refresh(village)

    resp = await client.get("/api/v1/administrative-areas", params={"level": "village"})
    assert resp.status_code == 200
    body = resp.json()
    assert all(item["level"] == "village" for item in body["items"])
    assert str(village.id) in {item["id"] for item in body["items"]}


@pytest.mark.asyncio
async def test_list_administrative_areas_filters_by_search(client, db):
    unique = uuid.uuid4().hex[:12]
    area = AdministrativeArea(name=f"Uniquename-{unique}", level=AdministrativeLevel.BLOCK)
    db.add(area)
    await db.commit()
    await db.refresh(area)

    resp = await client.get("/api/v1/administrative-areas", params={"search": unique})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == str(area.id)


@pytest.mark.asyncio
async def test_list_administrative_areas_is_paginated(client, db):
    resp = await client.get("/api/v1/administrative-areas", params={"limit": 1})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) <= 1
    assert "next_cursor" in body
