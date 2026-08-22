"""Full-stack end-to-end test: real server + ARQ worker + ML service + DB.

Requires the whole stack to be running (see README.md in this directory).
Skips (does not fail) if the server isn't reachable, so it's safe in CI
environments that don't spin up the full stack.
"""

import os
import time
import uuid

import httpx
import pytest

BASE_URL = os.environ.get("SERVER_BASE_URL", "http://localhost:8000/api/v1")


def _server_reachable() -> bool:
    try:
        resp = httpx.get(f"{BASE_URL}/health", timeout=2.0)
        return resp.status_code == 200
    except httpx.HTTPError:
        return False


pytestmark = pytest.mark.skipif(not _server_reachable(), reason=f"server not reachable at {BASE_URL}")


@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=15.0) as c:
        yield c


def test_full_duplicate_workflow_over_real_http(client):
    health = client.get("/health").json()
    assert health["database"] == "ok"
    assert health["redis"] == "ok"
    assert health["ml_service"] == "ok", "ML service must be reachable for this e2e test"

    # This test needs at least one administrative area to exist; it does not
    # create one (no admin API exists yet — see root README Known Limitations).
    # Skip gracefully if none is seeded.
    import asyncio
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "server"))
    from app.db.session import AsyncSessionLocal  # noqa: E402
    from app.models.administrative_area import AdministrativeArea  # noqa: E402
    from app.models.enums import AdministrativeLevel, Role  # noqa: E402
    from app.models.user import User  # noqa: E402
    from app.core.security import TokenType, create_token  # noqa: E402
    from sqlalchemy import select  # noqa: E402

    async def _setup():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(AdministrativeArea).limit(1))
            area = result.scalars().first()
            if area is None:
                area = AdministrativeArea(name="E2E Test State", level=AdministrativeLevel.STATE)
                db.add(area)
                await db.commit()
                await db.refresh(area)

            suffix = uuid.uuid4().hex[:8]
            citizen = User(phone=f"+91900{suffix}", name="E2E Citizen", role=Role.CITIZEN)
            officer = User(phone=f"+91901{suffix}", name="E2E Officer", role=Role.OFFICER)
            db.add_all([citizen, officer])
            await db.commit()
            await db.refresh(citizen)
            await db.refresh(officer)

            citizen_token, _ = create_token(
                user_id=citizen.id, role="citizen", token_type=TokenType.ACCESS, expires_minutes=15
            )
            officer_token, _ = create_token(
                user_id=officer.id, role="officer", token_type=TokenType.ACCESS, expires_minutes=15
            )
            return area.id, citizen_token, officer_token

    area_id, citizen_token, officer_token = asyncio.run(_setup())

    citizen_headers = {"Authorization": f"Bearer {citizen_token}"}
    officer_headers = {"Authorization": f"Bearer {officer_token}"}

    # A run-unique token keeps this run's pair unambiguously nearest to each
    # other, even though the dev DB accumulates challenges across test runs.
    token = uuid.uuid4().hex[:10]
    title = f"Overflowing drain near community hall {token}"
    description = (
        f"The drain near the community hall (ref {token}) has been overflowing for a week, "
        "attracting mosquitoes and creating a health hazard for residents nearby."
    )

    original = client.post(
        "/challenges",
        headers=citizen_headers,
        json={"title": title, "description": description, "administrative_area_id": str(area_id)},
    ).json()

    duplicate = client.post(
        "/challenges",
        headers=citizen_headers,
        json={"title": title, "description": description, "administrative_area_id": str(area_id)},
    ).json()

    # Give the real ARQ worker time to process the async embedding + candidate job.
    candidates = []
    for _ in range(15):
        time.sleep(1)
        candidates = client.get(
            f"/duplicate/challenges/{duplicate['id']}/candidates", headers=officer_headers
        ).json()
        if candidates:
            break

    assert candidates, "worker did not produce duplicate candidates in time"
    assert candidates[0]["candidate_challenge_id"] == original["id"]

    decision_resp = client.post(
        "/duplicate/decisions",
        headers=officer_headers,
        json={
            "challenge_id": duplicate["id"],
            "candidate_challenge_id": original["id"],
            "decision": "duplicate",
            "reason": "e2e test: identical report",
        },
    )
    assert decision_resp.status_code == 201

    updated = client.get(f"/challenges/{duplicate['id']}").json()
    assert updated["status"] == "duplicate"
    assert updated["duplicate_of_id"] == original["id"]

    # The system never deletes or merges — the original still exists untouched.
    original_after = client.get(f"/challenges/{original['id']}").json()
    assert original_after["status"] in ("submitted", "open")
