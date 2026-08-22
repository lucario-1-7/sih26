from __future__ import annotations

import uuid

from sqlalchemy import select

from app.core.pagination import paginate
from app.models.collaboration import Collaboration, CollaborationCommitment
from app.models.enums import CollaborationStatus, CollaborationType
from app.repositories.base import BaseRepository


class CollaborationRepository(BaseRepository):
    async def get(self, collaboration_id: uuid.UUID) -> Collaboration | None:
        return await self.db.get(Collaboration, collaboration_id)

    async def list_for_project(
        self, project_id: uuid.UUID, *, limit: int = 20, cursor: str | None = None
    ) -> tuple[list[Collaboration], str | None]:
        stmt = select(Collaboration).where(Collaboration.project_id == project_id)
        return await paginate(self.db, stmt, model=Collaboration, limit=limit, cursor=cursor)

    async def list_for_organization(
        self, organization_id: uuid.UUID, *, limit: int = 20, cursor: str | None = None
    ) -> tuple[list[Collaboration], str | None]:
        stmt = select(Collaboration).where(Collaboration.organization_id == organization_id)
        return await paginate(self.db, stmt, model=Collaboration, limit=limit, cursor=cursor)

    async def create(
        self, *, organization_id: uuid.UUID, project_id: uuid.UUID, type: CollaborationType, proposal: str | None
    ) -> Collaboration:
        collaboration = Collaboration(
            organization_id=organization_id,
            project_id=project_id,
            type=type,
            status=CollaborationStatus.INTERESTED,
            proposal=proposal,
        )
        self.db.add(collaboration)
        await self.db.flush()
        return collaboration


class CollaborationCommitmentRepository(BaseRepository):
    async def get(self, commitment_id: uuid.UUID) -> CollaborationCommitment | None:
        return await self.db.get(CollaborationCommitment, commitment_id)

    async def list_for_collaboration(
        self, collaboration_id: uuid.UUID, *, limit: int = 20, cursor: str | None = None
    ) -> tuple[list[CollaborationCommitment], str | None]:
        stmt = select(CollaborationCommitment).where(
            CollaborationCommitment.collaboration_id == collaboration_id
        )
        return await paginate(self.db, stmt, model=CollaborationCommitment, limit=limit, cursor=cursor)

    async def create(
        self,
        *,
        collaboration_id: uuid.UUID,
        type: CollaborationType,
        amount: float | None,
        currency: str | None,
        description: str | None,
    ) -> CollaborationCommitment:
        commitment = CollaborationCommitment(
            collaboration_id=collaboration_id, type=type, amount=amount, currency=currency, description=description
        )
        self.db.add(commitment)
        await self.db.flush()
        return commitment
