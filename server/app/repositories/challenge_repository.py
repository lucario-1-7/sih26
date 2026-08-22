from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.challenge import Challenge
from app.models.enums import ChallengeStatus
from app.repositories.base import BaseRepository


class ChallengeRepository(BaseRepository):
    async def get(self, challenge_id: uuid.UUID) -> Challenge | None:
        challenge = await self.db.get(Challenge, challenge_id)
        if challenge is None or challenge.deleted_at is not None:
            return None
        return challenge

    async def list(
        self,
        *,
        status: ChallengeStatus | None = None,
        submitted_by_id: uuid.UUID | None = None,
        cluster_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Challenge]:
        stmt = select(Challenge).where(Challenge.deleted_at.is_(None))
        if status is not None:
            stmt = stmt.where(Challenge.status == status)
        if submitted_by_id is not None:
            stmt = stmt.where(Challenge.submitted_by_id == submitted_by_id)
        if cluster_id is not None:
            stmt = stmt.where(Challenge.cluster_id == cluster_id)
        stmt = stmt.order_by(Challenge.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        *,
        title: str,
        description: str,
        submitted_by_id: uuid.UUID,
        administrative_area_id: uuid.UUID,
        pin_code: str | None,
    ) -> Challenge:
        challenge = Challenge(
            title=title,
            description=description,
            submitted_by_id=submitted_by_id,
            administrative_area_id=administrative_area_id,
            pin_code=pin_code,
        )
        self.db.add(challenge)
        await self.db.flush()
        return challenge

    async def find_nearest_by_embedding(
        self, *, embedding: list[float], exclude_id: uuid.UUID, limit: int
    ) -> list[Challenge]:
        """pgvector cosine-distance nearest-neighbor search, using the HNSW index."""
        stmt = (
            select(Challenge)
            .where(
                Challenge.id != exclude_id,
                Challenge.deleted_at.is_(None),
                Challenge.embedding.is_not(None),
            )
            .order_by(Challenge.embedding.cosine_distance(embedding))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
