from __future__ import annotations

import uuid

from sqlalchemy import select

from app.core.pagination import paginate
from app.models.enums import ProjectStatus
from app.models.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository):
    async def get(self, project_id: uuid.UUID) -> Project | None:
        project = await self.db.get(Project, project_id)
        if project is None or project.deleted_at is not None:
            return None
        return project

    async def list(
        self,
        *,
        cluster_id: uuid.UUID | None = None,
        status: ProjectStatus | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> tuple[list[Project], str | None]:
        stmt = select(Project).where(Project.deleted_at.is_(None))
        if cluster_id is not None:
            stmt = stmt.where(Project.cluster_id == cluster_id)
        if status is not None:
            stmt = stmt.where(Project.status == status)
        return await paginate(self.db, stmt, model=Project, limit=limit, cursor=cursor)

    async def create(
        self,
        *,
        cluster_id: uuid.UUID,
        title: str,
        description: str | None,
        owner_id: uuid.UUID,
        organization_id: uuid.UUID | None = None,
    ) -> Project:
        project = Project(
            cluster_id=cluster_id,
            title=title,
            description=description,
            owner_id=owner_id,
            organization_id=organization_id,
        )
        self.db.add(project)
        await self.db.flush()
        return project
