import pytest
from sqlalchemy import select

from app.models.audit_log import AuditLog
from app.models.challenge import Challenge
from app.models.enums import ChallengeStatus
from app.repositories.duplicate_repository import DuplicateRepository
from tests.conftest import auth_headers


async def _make_pair(db, administrative_area, citizen_user):
    original = Challenge(
        title="Pothole on main road near school",
        description="A large pothole has formed on the main road right outside the school gate.",
        submitted_by_id=citizen_user.id,
        administrative_area_id=administrative_area.id,
    )
    duplicate_report = Challenge(
        title="Big pothole near school entrance",
        description="There is a deep pothole on the road just outside the school entrance.",
        submitted_by_id=citizen_user.id,
        administrative_area_id=administrative_area.id,
    )
    db.add_all([original, duplicate_report])
    await db.commit()
    await db.refresh(original)
    await db.refresh(duplicate_report)

    await DuplicateRepository(db).create_candidate(
        challenge_id=duplicate_report.id,
        candidate_challenge_id=original.id,
        similarity_score=0.88,
        model_name="paraphrase-multilingual-MiniLM-L12-v2",
        model_version="1",
    )
    await db.commit()
    return original, duplicate_report


@pytest.mark.asyncio
async def test_initial_decision_marks_challenge_duplicate(
    client, db, administrative_area, citizen_user, validator_user
):
    original, duplicate_report = await _make_pair(db, administrative_area, citizen_user)

    resp = await client.post(
        "/api/v1/duplicate/decisions",
        json={
            "challenge_id": str(duplicate_report.id),
            "candidate_challenge_id": str(original.id),
            "decision": "duplicate",
        },
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 201

    resp = await client.get(f"/api/v1/challenges/{duplicate_report.id}")
    body = resp.json()
    assert body["status"] == "duplicate"
    assert body["duplicate_of_id"] == str(original.id)


@pytest.mark.asyncio
async def test_correction_reopens_challenge_and_is_the_current_effective_decision(
    client, db, administrative_area, citizen_user, validator_user
):
    original, duplicate_report = await _make_pair(db, administrative_area, citizen_user)

    await client.post(
        "/api/v1/duplicate/decisions",
        json={
            "challenge_id": str(duplicate_report.id),
            "candidate_challenge_id": str(original.id),
            "decision": "duplicate",
            "reason": "Looked like the same pothole.",
        },
        headers=auth_headers(validator_user),
    )

    resp = await client.post(
        "/api/v1/duplicate/decisions",
        json={
            "challenge_id": str(duplicate_report.id),
            "candidate_challenge_id": str(original.id),
            "decision": "not_duplicate",
            "reason": "Different road segment on closer review.",
        },
        headers=auth_headers(validator_user),
    )
    assert resp.status_code == 201
    correction_body = resp.json()
    assert correction_body["decision"] == "not_duplicate"

    # Current effective decision (derived from the latest record).
    latest = await DuplicateRepository(db).get_latest_decision(duplicate_report.id, original.id)
    assert latest.decision.value == "not_duplicate"
    assert str(latest.id) == correction_body["id"]

    resp = await client.get(f"/api/v1/challenges/{duplicate_report.id}")
    body = resp.json()
    assert body["status"] == "open"
    assert body["duplicate_of_id"] is None


@pytest.mark.asyncio
async def test_historical_decisions_are_preserved_never_updated_or_deleted(
    client, db, administrative_area, citizen_user, validator_user
):
    original, duplicate_report = await _make_pair(db, administrative_area, citizen_user)

    await client.post(
        "/api/v1/duplicate/decisions",
        json={
            "challenge_id": str(duplicate_report.id),
            "candidate_challenge_id": str(original.id),
            "decision": "duplicate",
        },
        headers=auth_headers(validator_user),
    )
    await client.post(
        "/api/v1/duplicate/decisions",
        json={
            "challenge_id": str(duplicate_report.id),
            "candidate_challenge_id": str(original.id),
            "decision": "not_duplicate",
        },
        headers=auth_headers(validator_user),
    )

    history = await DuplicateRepository(db).list_decisions(duplicate_report.id)
    assert len(history) == 2
    assert history[0].decision.value == "duplicate"
    assert history[1].decision.value == "not_duplicate"
    # The original row's own fields were never mutated.
    assert history[0].candidate_challenge_id == original.id


@pytest.mark.asyncio
async def test_unauthorized_user_cannot_correct_a_decision(
    client, db, administrative_area, citizen_user, validator_user
):
    original, duplicate_report = await _make_pair(db, administrative_area, citizen_user)

    await client.post(
        "/api/v1/duplicate/decisions",
        json={
            "challenge_id": str(duplicate_report.id),
            "candidate_challenge_id": str(original.id),
            "decision": "duplicate",
        },
        headers=auth_headers(validator_user),
    )

    resp = await client.post(
        "/api/v1/duplicate/decisions",
        json={
            "challenge_id": str(duplicate_report.id),
            "candidate_challenge_id": str(original.id),
            "decision": "not_duplicate",
        },
        headers=auth_headers(citizen_user),
    )
    assert resp.status_code == 403

    # The unauthorized attempt must not have changed anything.
    history = await DuplicateRepository(db).list_decisions(duplicate_report.id)
    assert len(history) == 1
    assert history[0].decision.value == "duplicate"


@pytest.mark.asyncio
async def test_correction_writes_an_audit_trail_linking_to_the_prior_decision(
    client, db, administrative_area, citizen_user, validator_user
):
    original, duplicate_report = await _make_pair(db, administrative_area, citizen_user)

    first = await client.post(
        "/api/v1/duplicate/decisions",
        json={
            "challenge_id": str(duplicate_report.id),
            "candidate_challenge_id": str(original.id),
            "decision": "duplicate",
        },
        headers=auth_headers(validator_user),
    )
    first_id = first.json()["id"]

    await client.post(
        "/api/v1/duplicate/decisions",
        json={
            "challenge_id": str(duplicate_report.id),
            "candidate_challenge_id": str(original.id),
            "decision": "not_duplicate",
        },
        headers=auth_headers(validator_user),
    )

    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.entity_id == duplicate_report.id, AuditLog.entity_type == "challenge")
        .order_by(AuditLog.created_at.asc())
    )
    logs = list(result.scalars().all())
    actions = [entry.action for entry in logs]
    assert "duplicate.decision" in actions
    assert "duplicate.decision.corrected" in actions

    correction_log = next(entry for entry in logs if entry.action == "duplicate.decision.corrected")
    assert correction_log.meta["corrects_decision_id"] == first_id
    assert correction_log.meta["previous_decision"] == "duplicate"
    assert correction_log.user_id == validator_user.id
