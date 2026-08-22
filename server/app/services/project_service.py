import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PROJECT_STATUS_TRANSITIONS, ProjectStatus, Role
from app.models.project import Project
from app.models.user import User
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
CROSS_ORGANIZATION_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={"detail": "Cannot manage another institution's project", "code": "FORBIDDEN"},
)


def _invalid_transition(current: ProjectStatus, target: ProjectStatus) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "detail": f"Cannot move a project from {current.value} to {target.value}",
            "code": "INVALID_STATUS_TRANSITION",
        },
    )


async def create_project(db: AsyncSession, *, data: ProjectCreate, actor: User) -> Project:
    cluster = await ClusterRepository(db).get(data.cluster_id)
    if cluster is None:
        raise CLUSTER_NOT_FOUND
    # organization_id is derived from the acting Coordinator's own
    # institution — never taken from the request body — so a Coordinator
    # cannot create a project attributed to another university.
    project = await ProjectRepository(db).create(
        cluster_id=data.cluster_id,
        title=data.title,
        description=data.description,
        owner_id=actor.id,
        organization_id=actor.organization_id,
    )
    await AuditRepository(db).log(
        user_id=actor.id, action="project.create", entity_type="project", entity_id=project.id
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
    cursor: str | None,
) -> tuple[list[Project], str | None]:
    return await ProjectRepository(db).list(
        cluster_id=cluster_id, status=status_filter, limit=limit, cursor=cursor
    )


async def update_project(
    db: AsyncSession, project_id: uuid.UUID, *, data: ProjectUpdate, actor: User
) -> Project:
    project = await ProjectRepository(db).get(project_id)
    if project is None:
        raise NOT_FOUND
    # Institutional isolation: a Coordinator/Faculty may only manage their own
    # university's projects. Superadmin is exempt (platform-wide scope).
    if actor.role != Role.SUPERADMIN and project.organization_id != actor.organization_id:
        raise CROSS_ORGANIZATION_FORBIDDEN
    if data.title is not None:
        project.title = data.title
    if data.description is not None:
        project.description = data.description
    if data.status is not None and data.status != project.status:
        if data.status not in PROJECT_STATUS_TRANSITIONS[project.status]:
            raise _invalid_transition(project.status, data.status)
        project.status = data.status
    await AuditRepository(db).log(
        user_id=actor.id, action="project.update", entity_type="project", entity_id=project.id
    )
    await db.commit()
    await db.refresh(project)  # onupdate=now() is server-computed — refresh before serializing
    return project
