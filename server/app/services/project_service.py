import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ProjectStatus
from app.models.project import Project
from app.repositories.audit_repository import AuditRepository
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate

NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Project not found", "code": "NOT_FOUND"}
)
CLUSTER_NOT_FOUND = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail={"detail": "cluster_id does not reference an existing cluster", "code": "INVALID_CLUSTER"},
)


async def create_project(db: AsyncSession, *, data: ProjectCreate, actor_id: uuid.UUID) -> Project:
    cluster = await ClusterRepository(db).get(data.cluster_id)
    if cluster is None:
        raise CLUSTER_NOT_FOUND
    project = await ProjectRepository(db).create(
        cluster_id=data.cluster_id, title=data.title, description=data.description, owner_id=actor_id
    )
    await AuditRepository(db).log(
        user_id=actor_id, action="project.create", entity_type="project", entity_id=project.id
    )
    await db.commit()
    return project


async def get_project(db: AsyncSession, project_id: uuid.UUID) -> Project:
    project = await ProjectRepository(db).get(project_id)
    if project is None:
        raise NOT_FOUND
    return project


async def list_projects(
    db: AsyncSession,
    *,
    cluster_id: uuid.UUID | None,
    status_filter: ProjectStatus | None,
    limit: int,
    offset: int,
) -> list[Project]:
    return await ProjectRepository(db).list(
        cluster_id=cluster_id, status=status_filter, limit=limit, offset=offset
    )


async def update_project(
    db: AsyncSession, project_id: uuid.UUID, *, data: ProjectUpdate, actor_id: uuid.UUID
) -> Project:
    project = await ProjectRepository(db).get(project_id)
    if project is None:
        raise NOT_FOUND
    if data.title is not None:
        project.title = data.title
    if data.description is not None:
        project.description = data.description
    if data.status is not None:
        project.status = data.status
    await AuditRepository(db).log(
        user_id=actor_id, action="project.update", entity_type="project", entity_id=project.id
    )
    await db.commit()
    return project
