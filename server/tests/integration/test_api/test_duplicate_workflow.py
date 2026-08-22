import pytest

from app.models.challenge import Challenge
from app.repositories.duplicate_repository import DuplicateRepository
from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_duplicate_decision_requires_human_review_and_is_never_automatic(
    client, db, administrative_area, citizen_user, validator_user
):
    original = Challenge(
        title="Broken streetlight near market",
        description="The streetlight near the main market has been broken for two weeks.",
        submitted_by_id=citizen_user.id,
        administrative_area_id=administrative_area.id,
    )
    duplicate_report = Challenge(
        title="Streetlight not working near bazaar",
        description="Street light close to the bazaar area has not worked for ten days.",
        submitted_by_id=citizen_user.id,
        administrative_area_id=administrative_area.id,
    )
    db.add_all([original, duplicate_report])
    await db.commit()
    await db.refresh(original)
    await db.refresh(duplicate_report)

    # Simulate what the async ML job would have produced (evidence only).
    await DuplicateRepository(db).create_candidate(
        challenge_id=duplicate_report.id,
        candidate_challenge_id=original.id,
        similarity_score=0.91,
        model_name="paraphrase-multilingual-MiniLM-L12-v2",
        model_version="1",
    )
    await db.commit()

    resp = await client.get(
        f"/api/v1/duplicate/challenges/{duplicate_report.id}/candidates",
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 200
    candidates = resp.json()
    assert len(candidates) == 1
    assert candidates[0]["candidate_challenge_id"] == str(original.id)

    # Citizens are not reviewers — cannot record a decision.
    resp = await client.post(
        "/api/v1/duplicate/decisions",
        json={
            "challenge_id": str(duplicate_report.id),
            "candidate_challenge_id": str(original.id),
            "decision": "duplicate",
        },
        headers=auth_headers(citizen_user),
    )
    assert resp.status_code == 403

    resp = await client.post(
        "/api/v1/duplicate/decisions",
        json={
            "challenge_id": str(duplicate_report.id),
            "candidate_challenge_id": str(original.id),
            "decision": "duplicate",
            "reason": "Same streetlight, same location.",
        },
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["decision"] == "duplicate"
    assert body["reviewer_id"] == str(validator_user.id)

    resp = await client.get(f"/api/v1/challenges/{duplicate_report.id}")
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["status"] == "duplicate"
    assert updated["duplicate_of_id"] == str(original.id)
    # The original challenge itself was never deleted or merged.
    resp_original = await client.get(f"/api/v1/challenges/{original.id}")
    assert resp_original.status_code == 200

    # A second decision on the same pair is not rejected — it's a correction.
    # The original decision row is never updated or deleted (append-only,
    # enforced at the DB level); this just appends a new record that becomes
    # the current effective decision. See test_duplicate_corrections.py for
    # full coverage of the correction workflow.
    resp = await client.post(
        "/api/v1/duplicate/decisions",
        json={
            "challenge_id": str(duplicate_report.id),
            "candidate_challenge_id": str(original.id),
            "decision": "not_duplicate",
        },
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 201

    resp = await client.get(f"/api/v1/challenges/{duplicate_report.id}")
    assert resp.status_code == 200
    corrected = resp.json()
    assert corrected["status"] == "open"
    assert corrected["duplicate_of_id"] is None
