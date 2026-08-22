import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deliverable import Deliverable
from app.models.enums import DeliverableStatus, Role
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.deliverable_repository import DeliverableRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.deliverable import DeliverableCreate, DeliverableUpdate

PROJECT_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Project not found", "code": "NOT_FOUND"}
)
DELIVERABLE_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Deliverable not found", "code": "NOT_FOUND"}
)
CROSS_ORGANIZATION_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={"detail": "Cannot manage deliverables of another institution's project", "code": "FORBIDDEN"},
)
NOT_PENDING_VERIFICATION = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={"detail": "Only a submitted deliverable can be verified", "code": "CONFLICT"},
)
VERIFICATION_REQUIRES_COORDINATOR = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={"detail": "Only a Coordinator or Superadmin can verify a deliverable", "code": "FORBIDDEN"},
)


async def _authorize_project(db: AsyncSession, project_id: uuid.UUID, actor: User):
    project = await ProjectRepository(db).get(project_id)
    if project is None:
        raise PROJECT_NOT_FOUND
    if actor.role != Role.SUPERADMIN and project.organization_id != actor.organization_id:
        raise CROSS_ORGANIZATION_FORBIDDEN
    return project


async def list_deliverables(
    db: AsyncSession, project_id: uuid.UUID, *, actor: User, limit: int, cursor: str | None
) -> tuple[list[Deliverable], str | None]:
    await _authorize_project(db, project_id, actor)
    return await DeliverableRepository(db).list_for_project(project_id, limit=limit, cursor=cursor)


async def create_deliverable(
    db: AsyncSession, project_id: uuid.UUID, *, data: DeliverableCreate, actor: User
) -> Deliverable:
    await _authorize_project(db, project_id, actor)
    deliverable = await DeliverableRepository(db).create(
        project_id=project_id, title=data.title, description=data.description, due_date=data.due_date
    )
    await AuditRepository(db).log(
        user_id=actor.id,
        action="deliverable.create",
        entity_type="deliverable",
        entity_id=deliverable.id,
        meta={"project_id": str(project_id)},
    )
    await db.commit()
    return deliverable


async def update_deliverable(
    db: AsyncSession,
    project_id: uuid.UUID,
    deliverable_id: uuid.UUID,
    *,
    data: DeliverableUpdate,
    actor: User,
) -> Deliverable:
    """Faculty/Coordinator updates content and, once evidence is attached,
    submits it for verification (status -> SUBMITTED)."""
    await _authorize_project(db, project_id, actor)
    deliverable_repo = DeliverableRepository(db)
    deliverable = await deliverable_repo.get(deliverable_id)
    if deliverable is None or deliverable.project_id != project_id:
        raise DELIVERABLE_NOT_FOUND

    if data.title is not None:
        deliverable.title = data.title
    if data.description is not None:
        deliverable.description = data.description
    if data.due_date is not None:
        deliverable.due_date = data.due_date
    if data.evidence is not None:
        deliverable.evidence = data.evidence
        deliverable.status = DeliverableStatus.SUBMITTED
        deliverable.submitted_at = datetime.now(timezone.utc)

    await AuditRepository(db).log(
        user_id=actor.id, action="deliverable.update", entity_type="deliverable", entity_id=deliverable.id
    )
    await db.commit()
    await db.refresh(deliverable)
    return deliverable


async def verify_deliverable(
    db: AsyncSession, project_id: uuid.UUID, deliverable_id: uuid.UUID, *, approve: bool, actor: User
) -> Deliverable:
    if actor.role not in (Role.COORDINATOR, Role.SUPERADMIN):
        raise VERIFICATION_REQUIRES_COORDINATOR
    await _authorize_project(db, project_id, actor)
    deliverable_repo = DeliverableRepository(db)
    deliverable = await deliverable_repo.get(deliverable_id)
    if deliverable is None or deliverable.project_id != project_id:
        raise DELIVERABLE_NOT_FOUND
    if deliverable.status != DeliverableStatus.SUBMITTED:
        raise NOT_PENDING_VERIFICATION

    deliverable.status = DeliverableStatus.VERIFIED if approve else DeliverableStatus.REJECTED
    deliverable.verified_at = datetime.now(timezone.utc)
    deliverable.verified_by_id = actor.id

    await AuditRepository(db).log(
        user_id=actor.id,
        action="deliverable.verified" if approve else "deliverable.rejected",
        entity_type="deliverable",
        entity_id=deliverable.id,
    )
    await db.commit()
    await db.refresh(deliverable)
    return deliverable
