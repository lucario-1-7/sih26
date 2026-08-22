import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import MilestoneStatus, Role
from app.models.milestone import Milestone
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.milestone_repository import MilestoneRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate

PROJECT_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Project not found", "code": "NOT_FOUND"}
)
MILESTONE_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Milestone not found", "code": "NOT_FOUND"}
)
CROSS_ORGANIZATION_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={"detail": "Cannot manage milestones of another institution's project", "code": "FORBIDDEN"},
)


async def _authorize_project(db: AsyncSession, project_id: uuid.UUID, actor: User):
    project = await ProjectRepository(db).get(project_id)
    if project is None:
        raise PROJECT_NOT_FOUND
    if actor.role != Role.SUPERADMIN and project.organization_id != actor.organization_id:
        raise CROSS_ORGANIZATION_FORBIDDEN
    return project


async def list_milestones(
    db: AsyncSession, project_id: uuid.UUID, *, actor: User, limit: int, cursor: str | None
) -> tuple[list[Milestone], str | None]:
    await _authorize_project(db, project_id, actor)
    return await MilestoneRepository(db).list_for_project(project_id, limit=limit, cursor=cursor)


async def create_milestone(
    db: AsyncSession, project_id: uuid.UUID, *, data: MilestoneCreate, actor: User
) -> Milestone:
    await _authorize_project(db, project_id, actor)
    milestone = await MilestoneRepository(db).create(
        project_id=project_id,
        title=data.title,
        description=data.description,
        due_date=data.due_date,
        order=data.order,
    )
    await AuditRepository(db).log(
        user_id=actor.id,
        action="milestone.create",
        entity_type="milestone",
        entity_id=milestone.id,
        meta={"project_id": str(project_id)},
    )
    await db.commit()
    return milestone


async def update_milestone(
    db: AsyncSession, project_id: uuid.UUID, milestone_id: uuid.UUID, *, data: MilestoneUpdate, actor: User
) -> Milestone:
    await _authorize_project(db, project_id, actor)
    milestone_repo = MilestoneRepository(db)
    milestone = await milestone_repo.get(milestone_id)
    if milestone is None or milestone.project_id != project_id:
        raise MILESTONE_NOT_FOUND

    if data.title is not None:
        milestone.title = data.title
    if data.description is not None:
        milestone.description = data.description
    if data.due_date is not None:
        milestone.due_date = data.due_date
    if data.order is not None:
        milestone.order = data.order

    completing = data.status is not None and data.status == MilestoneStatus.COMPLETED
    reopening = data.status is not None and data.status != MilestoneStatus.COMPLETED
    if data.status is not None:
        milestone.status = data.status
    if completing:
        milestone.completed_at = datetime.now(timezone.utc)
    elif reopening:
        milestone.completed_at = None

    await AuditRepository(db).log(
        user_id=actor.id,
        action="milestone.completed" if completing else "milestone.update",
        entity_type="milestone",
        entity_id=milestone.id,
    )
    await db.commit()
    await db.refresh(milestone)
    return milestone
