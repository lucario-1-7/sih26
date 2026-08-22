import uuid

from sqlalchemy import select

from app.models.duplicate import DuplicateCandidate, DuplicateDecision
from app.models.enums import DuplicateDecisionType
from app.repositories.base import BaseRepository


class DuplicateRepository(BaseRepository):
    async def create_candidate(
        self,
        *,
        challenge_id: uuid.UUID,
        candidate_challenge_id: uuid.UUID,
        similarity_score: float,
        model_name: str,
        model_version: str,
    ) -> DuplicateCandidate:
        candidate = DuplicateCandidate(
            challenge_id=challenge_id,
            candidate_challenge_id=candidate_challenge_id,
            similarity_score=similarity_score,
            model_name=model_name,
            model_version=model_version,
        )
        self.db.add(candidate)
        await self.db.flush()
        return candidate

    async def list_candidates(self, challenge_id: uuid.UUID) -> list[DuplicateCandidate]:
        stmt = (
            select(DuplicateCandidate)
            .where(DuplicateCandidate.challenge_id == challenge_id)
            .order_by(DuplicateCandidate.similarity_score.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_candidate(
        self, challenge_id: uuid.UUID, candidate_challenge_id: uuid.UUID
    ) -> DuplicateCandidate | None:
        stmt = select(DuplicateCandidate).where(
            DuplicateCandidate.challenge_id == challenge_id,
            DuplicateCandidate.candidate_challenge_id == candidate_challenge_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_decisions(self, challenge_id: uuid.UUID) -> list[DuplicateDecision]:
        stmt = select(DuplicateDecision).where(DuplicateDecision.challenge_id == challenge_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_decision(
        self,
        *,
        challenge_id: uuid.UUID,
        candidate_challenge_id: uuid.UUID,
        decision: DuplicateDecisionType,
        reviewer_id: uuid.UUID,
        reason: str | None,
    ) -> DuplicateDecision:
        record = DuplicateDecision(
            challenge_id=challenge_id,
            candidate_challenge_id=candidate_challenge_id,
            decision=decision,
            reviewer_id=reviewer_id,
            reason=reason,
        )
        self.db.add(record)
        await self.db.flush()
        return record
