import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collaboration import Collaboration, CollaborationCommitment
from app.models.enums import COLLABORATION_STATUS_TRANSITIONS, CollaborationStatus, CommitmentStatus, Role
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.collaboration_repository import CollaborationCommitmentRepository, CollaborationRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.collaboration import CollaborationCreate, CollaborationStatusUpdate, CommitmentCreate

PROJECT_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Project not found", "code": "NOT_FOUND"}
)
COLLABORATION_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Collaboration not found", "code": "NOT_FOUND"}
)
COMMITMENT_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Commitment not found", "code": "NOT_FOUND"}
)
CROSS_ORGANIZATION_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={"detail": "Cannot access another organization's collaboration", "code": "FORBIDDEN"},
)
UNIVERSITY_SCOPE_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={"detail": "Cannot manage another institution's collaboration", "code": "FORBIDDEN"},
)

_UNIVERSITY_ROLES = (Role.COORDINATOR, Role.FACULTY)

# Which actor (by role, on the *industry* side vs the *university* side) may
# effect each transition. Only the org that expressed interest may formalize
# it into a proposal; only the university side may accept/reject/advance it —
# an Industry user can never unilaterally decide a university accepted them.
_TRANSITION_ACTOR = {
    (CollaborationStatus.INTERESTED, CollaborationStatus.PROPOSED): "industry",
    (CollaborationStatus.INTERESTED, CollaborationStatus.REJECTED): "university",
    (CollaborationStatus.PROPOSED, CollaborationStatus.ACCEPTED): "university",
    (CollaborationStatus.PROPOSED, CollaborationStatus.REJECTED): "university",
    (CollaborationStatus.ACCEPTED, CollaborationStatus.ACTIVE): "university",
    (CollaborationStatus.ACCEPTED, CollaborationStatus.REJECTED): "university",
    (CollaborationStatus.ACTIVE, CollaborationStatus.COMPLETED): "university",
}


def _invalid_transition(current: CollaborationStatus, target: CollaborationStatus) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "detail": f"Cannot move a collaboration from {current.value} to {target.value}",
            "code": "INVALID_STATUS_TRANSITION",
        },
    )


async def create_collaboration(db: AsyncSession, *, data: CollaborationCreate, actor: User) -> Collaboration:
    project = await ProjectRepository(db).get(data.project_id)
    if project is None:
        raise PROJECT_NOT_FOUND
    collaboration = await CollaborationRepository(db).create(
        organization_id=actor.organization_id,
        project_id=data.project_id,
        type=data.type,
        proposal=None,
    )
    await AuditRepository(db).log(
        user_id=actor.id,
        action="collaboration.create",
        entity_type="collaboration",
        entity_id=collaboration.id,
        meta={"project_id": str(data.project_id), "type": data.type.value},
    )
    await db.commit()
    return collaboration


async def list_collaborations_for_project(
    db: AsyncSession, project_id: uuid.UUID, *, limit: int, cursor: str | None
) -> tuple[list[Collaboration], str | None]:
    return await CollaborationRepository(db).list_for_project(project_id, limit=limit, cursor=cursor)


async def list_collaborations_for_my_organization(
    db: AsyncSession, *, actor: User, limit: int, cursor: str | None
) -> tuple[list[Collaboration], str | None]:
    return await CollaborationRepository(db).list_for_organization(
        actor.organization_id, limit=limit, cursor=cursor
    )


async def update_collaboration_status(
    db: AsyncSession, collaboration_id: uuid.UUID, *, data: CollaborationStatusUpdate, actor: User
) -> Collaboration:
    collab_repo = CollaborationRepository(db)
    collaboration = await collab_repo.get(collaboration_id)
    if collaboration is None:
        raise COLLABORATION_NOT_FOUND

    if collaboration.status == data.status:
        return collaboration

    if data.status not in COLLABORATION_STATUS_TRANSITIONS.get(collaboration.status, frozenset()):
        raise _invalid_transition(collaboration.status, data.status)

    side = _TRANSITION_ACTOR.get((collaboration.status, data.status))
    if side == "industry":
        if actor.role != Role.INDUSTRY or actor.organization_id != collaboration.organization_id:
            raise CROSS_ORGANIZATION_FORBIDDEN
    elif side == "university":
        if actor.role == Role.SUPERADMIN:
            pass
        else:
            project = await ProjectRepository(db).get(collaboration.project_id)
            if (
                actor.role not in _UNIVERSITY_ROLES
                or project is None
                or project.organization_id != actor.organization_id
            ):
                raise UNIVERSITY_SCOPE_FORBIDDEN

    collaboration.status = data.status
    if data.proposal is not None:
        collaboration.proposal = data.proposal

    await AuditRepository(db).log(
        user_id=actor.id,
        action="collaboration.status_changed",
        entity_type="collaboration",
        entity_id=collaboration.id,
        meta={"status": data.status.value},
    )
    await db.commit()
    await db.refresh(collaboration)
    return collaboration


async def create_commitment(
    db: AsyncSession, collaboration_id: uuid.UUID, *, data: CommitmentCreate, actor: User
) -> CollaborationCommitment:
    collaboration = await CollaborationRepository(db).get(collaboration_id)
    if collaboration is None:
        raise COLLABORATION_NOT_FOUND
    if actor.role != Role.INDUSTRY or actor.organization_id != collaboration.organization_id:
        raise CROSS_ORGANIZATION_FORBIDDEN

    commitment = await CollaborationCommitmentRepository(db).create(
        collaboration_id=collaboration_id,
        type=data.type,
        amount=data.amount,
        currency=data.currency,
        description=data.description,
    )
    await AuditRepository(db).log(
        user_id=actor.id,
        action="collaboration_commitment.create",
        entity_type="collaboration_commitment",
        entity_id=commitment.id,
        meta={"collaboration_id": str(collaboration_id), "type": data.type.value},
    )
    await db.commit()
    return commitment


async def list_commitments(
    db: AsyncSession, collaboration_id: uuid.UUID, *, limit: int, cursor: str | None
) -> tuple[list[CollaborationCommitment], str | None]:
    return await CollaborationCommitmentRepository(db).list_for_collaboration(
        collaboration_id, limit=limit, cursor=cursor
    )


async def update_commitment_status(
    db: AsyncSession,
    collaboration_id: uuid.UUID,
    commitment_id: uuid.UUID,
    *,
    new_status: CommitmentStatus,
    evidence: str | None,
    actor: User,
) -> CollaborationCommitment:
    """Only the university side of the collaboration (Coordinator/Faculty of
    the project's own institution, or Superadmin) may accept/fulfill/reject a
    commitment — Industry proposes, the university reviews."""
    collaboration = await CollaborationRepository(db).get(collaboration_id)
    if collaboration is None:
        raise COLLABORATION_NOT_FOUND

    if actor.role != Role.SUPERADMIN:
        project = await ProjectRepository(db).get(collaboration.project_id)
        if (
            actor.role not in _UNIVERSITY_ROLES
            or project is None
            or project.organization_id != actor.organization_id
        ):
            raise UNIVERSITY_SCOPE_FORBIDDEN

    commitment_repo = CollaborationCommitmentRepository(db)
    commitment = await commitment_repo.get(commitment_id)
    if commitment is None or commitment.collaboration_id != collaboration_id:
        raise COMMITMENT_NOT_FOUND

    commitment.status = new_status
    if evidence is not None:
        commitment.evidence = evidence

    await AuditRepository(db).log(
        user_id=actor.id,
        action="collaboration_commitment.status_changed",
        entity_type="collaboration_commitment",
        entity_id=commitment.id,
        meta={"status": new_status.value},
    )
    await db.commit()
    await db.refresh(commitment)
    return commitment
