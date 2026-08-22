import uuid

import pytest

from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_list_clusters_cursor_pagination_end_to_end(client, validator_user):
    created_ids = []
    for i in range(5):
        resp = await client.post(
            "/api/v1/clusters",
            json={"title": f"Cursor E2E Test Cluster {uuid.uuid4().hex[:8]} {i}"},
            headers=auth_headers(validator_user),
        )
        assert resp.status_code == 201
        created_ids.append(resp.json()["id"])
    newest_first = list(reversed(created_ids))

    # First page: no cursor query param at all.
    resp = await client.get("/api/v1/clusters", params={"limit": 2})
    assert resp.status_code == 200
    body = resp.json()
    assert [item["id"] for item in body["items"]] == newest_first[:2]
    assert body["next_cursor"] is not None
    # Cursor is opaque — not a small integer offset.
    assert not body["next_cursor"].isdigit()

    seen = [item["id"] for item in body["items"]]
    cursor = body["next_cursor"]
    for _ in range(1000):
        resp = await client.get("/api/v1/clusters", params={"limit": 2, "cursor": cursor})
        assert resp.status_code == 200
        body = resp.json()
        seen.extend(item["id"] for item in body["items"])
        cursor = body["next_cursor"]
        if cursor is None:
            break
    else:
        pytest.fail("pagination never reached end of collection")

    assert len(seen) == len(set(seen))  # no item repeated across pages
    assert seen[:5] == newest_first  # deterministic, stable order


@pytest.mark.asyncio
async def test_malformed_cursor_returns_422_not_500(client):
    resp = await client.get("/api/v1/clusters", params={"cursor": "!!not-base64!!"})
    assert resp.status_code == 422
    body = resp.json()
    assert body["code"] == "INVALID_CURSOR"


@pytest.mark.asyncio
async def test_offset_query_param_no_longer_accepted(client):
    """Regression: offset-based pagination must be fully removed, not just hidden."""
    resp = await client.get("/api/v1/clusters", params={"offset": 20, "limit": 5})
    assert resp.status_code == 200
    # `offset` is simply an unrecognized/ignored query param now — the route
    # no longer has an `offset` parameter, so this must not raise, and results
    # must be identical to the same call without it.
    resp_without = await client.get("/api/v1/clusters", params={"limit": 5})
    assert [i["id"] for i in resp.json()["items"]] == [i["id"] for i in resp_without.json()["items"]]
