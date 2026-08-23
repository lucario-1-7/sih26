import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.challenge import Challenge
from app.models.enums import ChallengeStatus, Role
from app.models.user import User
from app.repositories.administrative_area_repository import AdministrativeAreaRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.cluster_repository import ClusterRepository
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
NOT_OWNER = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={"detail": "Only the submitter can edit challenge content", "code": "FORBIDDEN"},
)
SEVERITY_REQUIRES_VALIDATOR = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={"detail": "Only a VALIDATOR can set challenge severity", "code": "FORBIDDEN"},
)
CLUSTERING_REQUIRES_VALIDATOR = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={"detail": "Only a VALIDATOR or SUPERADMIN can assign a challenge to a cluster", "code": "FORBIDDEN"},
)
CLUSTER_NOT_FOUND = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail={"detail": "cluster_id does not reference an existing cluster", "code": "INVALID_CLUSTER"},
)

logger = logging.getLogger("app.challenges")


async def create_challenge(db: AsyncSession, *, data: ChallengeCreate, actor: User) -> Challenge:
    area = await AdministrativeAreaRepository(db).get(data.administrative_area_id)
    if area is None:
        raise AREA_NOT_FOUND

    # on_behalf_of_* only ever applies to a FIELD_ASSISTANT submission — the
    # citizen being reported for has no account of their own. Silently
    # dropped for a CITIZEN's own submission rather than erroring, since a
    # client-supplied value there would be meaningless, not malicious.
    is_assisted = actor.role == Role.FIELD_ASSISTANT
    challenge = await ChallengeRepository(db).create(
        title=data.title,
        description=data.description,
        submitted_by_id=actor.id,
        administrative_area_id=data.administrative_area_id,
        pin_code=data.pin_code,
        on_behalf_of_name=data.on_behalf_of_name if is_assisted else None,
        on_behalf_of_phone=data.on_behalf_of_phone if is_assisted else None,
    )
    await AuditRepository(db).log(
        user_id=actor.id, action="challenge.create", entity_type="challenge", entity_id=challenge.id
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
    cursor: str | None,
) -> tuple[list[Challenge], str | None]:
    return await ChallengeRepository(db).list(
        status=status_filter,
        submitted_by_id=submitted_by_id,
        cluster_id=cluster_id,
        limit=limit,
        cursor=cursor,
    )


async def update_challenge(
    db: AsyncSession, challenge_id: uuid.UUID, *, data: ChallengeUpdate, actor: User
) -> Challenge:
    """Content fields (title/description) are owner-only — a CITIZEN or
    FIELD_ASSISTANT may only edit their own submission. `severity` and
    `cluster_id` are VALIDATOR/SUPERADMIN-only fields (government review
    responsibility) and are not subject to the owner/status checks that gate
    content edits."""
    challenge = await ChallengeRepository(db).get(challenge_id)
    if challenge is None:
        raise NOT_FOUND

    content_edited = data.title is not None or data.description is not None
    if content_edited:
        if challenge.submitted_by_id != actor.id:
            raise NOT_OWNER
        if challenge.status not in (ChallengeStatus.SUBMITTED, ChallengeStatus.OPEN):
            raise NOT_MUTABLE
        if data.title is not None:
            challenge.title = data.title
        if data.description is not None:
            challenge.description = data.description

    if data.severity is not None:
        if actor.role != Role.VALIDATOR:
            raise SEVERITY_REQUIRES_VALIDATOR
        challenge.severity = data.severity

    if data.cluster_id is not None:
        if actor.role not in (Role.VALIDATOR, Role.SUPERADMIN):
            raise CLUSTERING_REQUIRES_VALIDATOR
        cluster = await ClusterRepository(db).get(data.cluster_id)
        if cluster is None:
            raise CLUSTER_NOT_FOUND
        challenge.cluster_id = data.cluster_id

    await AuditRepository(db).log(
        user_id=actor.id, action="challenge.update", entity_type="challenge", entity_id=challenge.id
    )
    await db.commit()
    # `updated_at`'s onupdate value is computed server-side by the UPDATE
    # statement — without a refresh it's left expired, and a later sync
    # attribute access (e.g. Pydantic serialization) would crash with
    # MissingGreenlet trying to lazy-load it outside an awaited context.
    await db.refresh(challenge)
    return challenge
