import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import Role
from app.models.project_participant import ProjectParticipant
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.project_participant_repository import ProjectParticipantRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.project_participant import ProjectParticipantCreate, ProjectParticipantUpdate

PROJECT_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Project not found", "code": "NOT_FOUND"}
)
PARTICIPANT_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail={"detail": "Project participant not found", "code": "NOT_FOUND"},
)
CROSS_ORGANIZATION_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={"detail": "Cannot manage participants of another institution's project", "code": "FORBIDDEN"},
)


async def _authorize_project_access(db: AsyncSession, project_id: uuid.UUID, actor: User):
    project = await ProjectRepository(db).get(project_id)
    if project is None:
        raise PROJECT_NOT_FOUND
    if actor.role != Role.SUPERADMIN and project.organization_id != actor.organization_id:
        raise CROSS_ORGANIZATION_FORBIDDEN
    return project


async def list_participants(
    db: AsyncSession, project_id: uuid.UUID, *, actor: User, limit: int, cursor: str | None
) -> tuple[list[ProjectParticipant], str | None]:
    await _authorize_project_access(db, project_id, actor)
    return await ProjectParticipantRepository(db).list_for_project(project_id, limit=limit, cursor=cursor)


async def create_participant(
    db: AsyncSession, project_id: uuid.UUID, *, data: ProjectParticipantCreate, actor: User
) -> ProjectParticipant:
    await _authorize_project_access(db, project_id, actor)
    participant = await ProjectParticipantRepository(db).create(
        project_id=project_id,
        name=data.name,
        department=data.department,
        academic_year=data.academic_year,
        registration_id=data.registration_id,
        participation_role=data.participation_role,
    )
    await AuditRepository(db).log(
        user_id=actor.id,
        action="project_participant.create",
        entity_type="project_participant",
        entity_id=participant.id,
        meta={"project_id": str(project_id)},
    )
    await db.commit()
    return participant


async def update_participant(
    db: AsyncSession,
    project_id: uuid.UUID,
    participant_id: uuid.UUID,
    *,
    data: ProjectParticipantUpdate,
    actor: User,
) -> ProjectParticipant:
    await _authorize_project_access(db, project_id, actor)
    participant_repo = ProjectParticipantRepository(db)
    participant = await participant_repo.get(participant_id)
    if participant is None or participant.project_id != project_id:
        raise PARTICIPANT_NOT_FOUND

    if data.name is not None:
        participant.name = data.name
    if data.department is not None:
        participant.department = data.department
    if data.academic_year is not None:
        participant.academic_year = data.academic_year
    if data.registration_id is not None:
        participant.registration_id = data.registration_id
    if data.participation_role is not None:
        participant.participation_role = data.participation_role
    if data.is_active is not None:
        participant.is_active = data.is_active

    await AuditRepository(db).log(
        user_id=actor.id,
        action="project_participant.update",
        entity_type="project_participant",
        entity_id=participant.id,
    )
    await db.commit()
    await db.refresh(participant)  # onupdate=now() is server-computed — refresh before serializing
    return participant
