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


async def list_candidates(db: AsyncSession, challenge_id: uuid.UUID) -> list[DuplicateCandidate]:
    return await DuplicateRepository(db).list_candidates(challenge_id)


async def _recompute_challenge_status(dup_repo: DuplicateRepository, challenge) -> None:
    """Derives current effective status purely from the latest decision per
    candidate pair — never from the full history — so a correction (a new
    append-only row) can reopen a challenge that a prior decision had marked
    DUPLICATE, or re-mark one that a prior decision had cleared."""
    history = await dup_repo.list_decisions(challenge.id)
    latest_by_candidate: dict[uuid.UUID, DuplicateDecision] = {}
    for d in history:  # oldest first — later entries overwrite earlier ones
        latest_by_candidate[d.candidate_challenge_id] = d

    duplicate_decision = next(
        (d for d in latest_by_candidate.values() if d.decision == DuplicateDecisionType.DUPLICATE),
        None,
    )
    if duplicate_decision is not None:
        challenge.status = ChallengeStatus.DUPLICATE
        challenge.duplicate_of_id = duplicate_decision.candidate_challenge_id
        return

    challenge.duplicate_of_id = None
    all_candidates = await dup_repo.list_candidates(challenge.id)
    unresolved = [c for c in all_candidates if c.candidate_challenge_id not in latest_by_candidate]
    if not unresolved and challenge.status in (ChallengeStatus.SUBMITTED, ChallengeStatus.DUPLICATE):
        challenge.status = ChallengeStatus.OPEN


async def decide(
    db: AsyncSession, *, data: DuplicateDecisionCreate, reviewer_id: uuid.UUID
) -> DuplicateDecision:
    """Records a human DUPLICATE / NOT_DUPLICATE decision.

    Decisions are append-only and immutable (enforced at the DB level — see
    `database/alembic/versions/c64f1440c539_*.py`). A second decision on the
    same candidate pair is not rejected: it is a *correction* — a new record
    that becomes the current effective decision, while the original row is
    preserved untouched for the audit trail. This satisfies both halves of
    "auditable and reversible": nothing is ever updated or deleted, but an
    authorized reviewer can still correct a prior call.
    """
    dup_repo = DuplicateRepository(db)
    challenge_repo = ChallengeRepository(db)

    candidate = await dup_repo.get_candidate(data.challenge_id, data.candidate_challenge_id)
    if candidate is None:
        raise CANDIDATE_NOT_FOUND

    previous_decision = await dup_repo.get_latest_decision(
        data.challenge_id, data.candidate_challenge_id
    )
    is_correction = previous_decision is not None

    decision = await dup_repo.create_decision(
        challenge_id=data.challenge_id,
        candidate_challenge_id=data.candidate_challenge_id,
        decision=data.decision,
        reviewer_id=reviewer_id,
        reason=data.reason,
    )

    challenge = await challenge_repo.get(data.challenge_id)
    if challenge is not None:
        await _recompute_challenge_status(dup_repo, challenge)

    meta = {
        "candidate_challenge_id": str(data.candidate_challenge_id),
        "decision": data.decision.value,
        "reason": data.reason,
    }
    if is_correction:
        meta["corrects_decision_id"] = str(previous_decision.id)
        meta["previous_decision"] = previous_decision.decision.value

    await AuditRepository(db).log(
        user_id=reviewer_id,
        action="duplicate.decision.corrected" if is_correction else "duplicate.decision",
        entity_type="challenge",
        entity_id=data.challenge_id,
        meta=meta,
    )
    await db.commit()
    return decision
