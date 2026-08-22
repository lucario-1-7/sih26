import uuid

import pytest

from app.services import ml_client
from app.services.ml_client import MLServiceError
from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_ml_service_unreachable_returns_503_not_500(client, superadmin_user, monkeypatch):
    async def _raise_unreachable(*args, **kwargs):
        raise MLServiceError(
            "embedding request failed: [Errno 111] Connection refused to http://internal-ml-host:8001"
        )

    monkeypatch.setattr(ml_client, "embed_text", _raise_unreachable)

    resp = await client.post(
        "/api/v1/matching/organizations",
        json={
            "name": f"Unreachable ML Test Org {uuid.uuid4().hex[:8]}",
            "type": "university",
            "domain_tags": ["civil-engineering"],
        },
        headers=auth_headers(superadmin_user),
    )

    assert resp.status_code == 503
    body = resp.json()
    assert body["code"] == "ML_SERVICE_UNAVAILABLE"
    assert "request_id" in body
    # Internal connection details/stack traces must never reach the client.
    assert "internal-ml-host" not in body["detail"]
    assert "Errno" not in body["detail"]
    assert "Traceback" not in body["detail"]


@pytest.mark.asyncio
async def test_ml_service_unreachable_does_not_persist_a_partial_organization(
    client, db, superadmin_user, monkeypatch
):
    from sqlalchemy import select

    from app.models.organization import Organization

    async def _raise_unreachable(*args, **kwargs):
        raise MLServiceError("connection refused")

    monkeypatch.setattr(ml_client, "embed_text", _raise_unreachable)

    org_name = f"Unreachable ML No Persist Test Org {uuid.uuid4().hex[:8]}"
    resp = await client.post(
        "/api/v1/matching/organizations",
        json={"name": org_name, "type": "industry", "domain_tags": []},
        headers=auth_headers(superadmin_user),
    )
    assert resp.status_code == 503

    result = await db.execute(select(Organization).where(Organization.name == org_name))
    assert result.scalar_one_or_none() is None
