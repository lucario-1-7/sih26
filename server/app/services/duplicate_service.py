import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.duplicate import DuplicateCandidate, DuplicateDecision
from app.models.enums import ChallengeStatus, DuplicateDecisionType
from app.repositories.audit_repository import AuditRepository
from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.duplicate_repository import DuplicateRepository
from app.schemas.duplicate import DuplicateDecisionCreate

CANDIDATE_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail={"detail": "No such duplicate candidate for this challenge", "code": "NOT_FOUND"},
)
ALREADY_DECIDED = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={"detail": "This candidate pair already has a decision", "code": "CONFLICT"},
)


async def list_candidates(db: AsyncSession, challenge_id: uuid.UUID) -> list[DuplicateCandidate]:
    return await DuplicateRepository(db).list_candidates(challenge_id)


async def decide(
    db: AsyncSession, *, data: DuplicateDecisionCreate, reviewer_id: uuid.UUID
) -> DuplicateDecision:
    dup_repo = DuplicateRepository(db)
    challenge_repo = ChallengeRepository(db)

    candidate = await dup_repo.get_candidate(data.challenge_id, data.candidate_challenge_id)
    if candidate is None:
        raise CANDIDATE_NOT_FOUND

    existing_decisions = {
        d.candidate_challenge_id for d in await dup_repo.list_decisions(data.challenge_id)
    }
    if data.candidate_challenge_id in existing_decisions:
        raise ALREADY_DECIDED

    decision = await dup_repo.create_decision(
        challenge_id=data.challenge_id,
        candidate_challenge_id=data.candidate_challenge_id,
        decision=data.decision,
        reviewer_id=reviewer_id,
        reason=data.reason,
    )

    challenge = await challenge_repo.get(data.challenge_id)
    if challenge is not None:
        if data.decision == DuplicateDecisionType.DUPLICATE:
            # Human decision only — the system never auto-merges. This links the
            # challenge to the reviewer-confirmed original without deleting anything.
            challenge.status = ChallengeStatus.DUPLICATE
            challenge.duplicate_of_id = data.candidate_challenge_id
        else:
            all_candidates = await dup_repo.list_candidates(data.challenge_id)
            all_decisions = {
                d.candidate_challenge_id for d in await dup_repo.list_decisions(data.challenge_id)
            } | {data.candidate_challenge_id}
            unresolved = [c for c in all_candidates if c.candidate_challenge_id not in all_decisions]
            if not unresolved and challenge.status == ChallengeStatus.SUBMITTED:
                challenge.status = ChallengeStatus.OPEN

    await AuditRepository(db).log(
        user_id=reviewer_id,
        action="duplicate.decision",
        entity_type="challenge",
        entity_id=data.challenge_id,
        meta={
            "candidate_challenge_id": str(data.candidate_challenge_id),
            "decision": data.decision.value,
            "reason": data.reason,
        },
    )
    await db.commit()
    return decision
