import pytest

from app.models.challenge import Challenge
from app.models.enums import ChallengeStatus
from app.repositories.duplicate_repository import DuplicateRepository
from app.workers.tasks import generate_duplicate_candidates


@pytest.mark.asyncio
async def test_duplicate_job_is_idempotent(db, administrative_area, citizen_user):
    original = Challenge(
        title="Overflowing garbage bin at bus stand",
        description="The garbage bin at the main bus stand has been overflowing for a week and smells bad.",
        submitted_by_id=citizen_user.id,
        administrative_area_id=administrative_area.id,
    )
    similar = Challenge(
        title="Garbage overflow near bus stop",
        description="Trash bin near the bus stop is overflowing for many days causing a bad smell.",
        submitted_by_id=citizen_user.id,
        administrative_area_id=administrative_area.id,
    )
    db.add_all([original, similar])
    await db.commit()
    await db.refresh(original)
    await db.refresh(similar)

    await generate_duplicate_candidates(None, str(similar.id))
    first_run_candidates = await DuplicateRepository(db).list_candidates(similar.id)

    # Re-running must not create duplicate rows or error out.
    await generate_duplicate_candidates(None, str(similar.id))
    second_run_candidates = await DuplicateRepository(db).list_candidates(similar.id)

    assert len(first_run_candidates) == len(second_run_candidates)

    ids_seen = [c.candidate_challenge_id for c in second_run_candidates]
    assert len(ids_seen) == len(set(ids_seen))  # no duplicate rows for the same pair

    await db.refresh(similar)
    assert similar.embedding is not None
    assert len(similar.embedding) == 384


@pytest.mark.asyncio
async def test_duplicate_job_handles_missing_challenge_gracefully():
    import uuid

    await generate_duplicate_candidates(None, str(uuid.uuid4()))  # must not raise
