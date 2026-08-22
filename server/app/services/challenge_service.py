import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.challenge import Challenge
from app.models.enums import ChallengeStatus
from app.repositories.administrative_area_repository import AdministrativeAreaRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.challenge_repository import ChallengeRepository
from app.schemas.challenge import ChallengeCreate, ChallengeUpdate
from app.services.job_queue import enqueue_duplicate_candidate_generation

NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Challenge not found", "code": "NOT_FOUND"}
)
AREA_NOT_FOUND = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail={
        "detail": "administrative_area_id does not reference an existing administrative area",
        "code": "INVALID_ADMINISTRATIVE_AREA",
    },
)
NOT_MUTABLE = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={"detail": "Challenge can no longer be edited in its current status", "code": "CONFLICT"},
)

logger = logging.getLogger("app.challenges")


async def create_challenge(db: AsyncSession, *, data: ChallengeCreate, actor_id: uuid.UUID) -> Challenge:
    area = await AdministrativeAreaRepository(db).get(data.administrative_area_id)
    if area is None:
        raise AREA_NOT_FOUND

    challenge = await ChallengeRepository(db).create(
        title=data.title,
        description=data.description,
        submitted_by_id=actor_id,
        administrative_area_id=data.administrative_area_id,
        pin_code=data.pin_code,
    )
    await AuditRepository(db).log(
        user_id=actor_id, action="challenge.create", entity_type="challenge", entity_id=challenge.id
    )
    await db.commit()

    # Enqueued only after the transaction commits, so the worker can see the row.
    # The challenge was already durably persisted above — if Redis is briefly
    # unreachable here, the request must not report failure for a resource
    # that was in fact created. It's simply left pending duplicate-candidate
    # processing (status stays SUBMITTED) rather than surfacing a false 500.
    try:
        await enqueue_duplicate_candidate_generation(str(challenge.id))
    except Exception:
        logger.error(
            "Failed to enqueue duplicate-candidate job for challenge %s; "
            "it will remain SUBMITTED until reprocessed.",
            challenge.id,
            exc_info=True,
        )
    return challenge


async def get_challenge(db: AsyncSession, challenge_id: uuid.UUID) -> Challenge:
    challenge = await ChallengeRepository(db).get(challenge_id)
    if challenge is None:
        raise NOT_FOUND
    return challenge


async def list_challenges(
    db: AsyncSession,
    *,
    status_filter: ChallengeStatus | None,
    submitted_by_id: uuid.UUID | None,
    cluster_id: uuid.UUID | None,
    limit: int,
    offset: int,
) -> list[Challenge]:
    return await ChallengeRepository(db).list(
        status=status_filter,
        submitted_by_id=submitted_by_id,
        cluster_id=cluster_id,
        limit=limit,
        offset=offset,
    )


async def update_challenge(
    db: AsyncSession, challenge_id: uuid.UUID, *, data: ChallengeUpdate, actor_id: uuid.UUID
) -> Challenge:
    challenge = await ChallengeRepository(db).get(challenge_id)
    if challenge is None:
        raise NOT_FOUND
    if challenge.status not in (ChallengeStatus.SUBMITTED, ChallengeStatus.OPEN):
        raise NOT_MUTABLE
    if data.title is not None:
        challenge.title = data.title
    if data.description is not None:
        challenge.description = data.description
    await AuditRepository(db).log(
        user_id=actor_id, action="challenge.update", entity_type="challenge", entity_id=challenge.id
    )
    await db.commit()
    return challenge
