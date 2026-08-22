import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import Role
from app.models.impact_indicator import ImpactIndicator
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.impact_indicator_repository import ImpactIndicatorRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.impact_indicator import ImpactIndicatorCreate, ImpactIndicatorEndlineUpdate

PROJECT_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Project not found", "code": "NOT_FOUND"}
)
INDICATOR_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Impact indicator not found", "code": "NOT_FOUND"}
)
CROSS_ORGANIZATION_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={"detail": "Cannot manage impact indicators of another institution's project", "code": "FORBIDDEN"},
)
VERIFICATION_REQUIRES_VALIDATOR = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={"detail": "Only a Validator or Superadmin can verify impact", "code": "FORBIDDEN"},
)
ENDLINE_NOT_SET = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={"detail": "Cannot verify an indicator with no claimed endline value yet", "code": "CONFLICT"},
)


async def _authorize_project(db: AsyncSession, project_id: uuid.UUID, actor: User):
    project = await ProjectRepository(db).get(project_id)
    if project is None:
        raise PROJECT_NOT_FOUND
    if actor.role != Role.SUPERADMIN and project.organization_id != actor.organization_id:
        raise CROSS_ORGANIZATION_FORBIDDEN
    return project


async def list_indicators(
    db: AsyncSession, project_id: uuid.UUID, *, actor: User, limit: int, cursor: str | None
) -> tuple[list[ImpactIndicator], str | None]:
    await _authorize_project(db, project_id, actor)
    return await ImpactIndicatorRepository(db).list_for_project(project_id, limit=limit, cursor=cursor)


async def create_indicator(
    db: AsyncSession, project_id: uuid.UUID, *, data: ImpactIndicatorCreate, actor: User
) -> ImpactIndicator:
    await _authorize_project(db, project_id, actor)
    indicator = await ImpactIndicatorRepository(db).create(
        project_id=project_id,
        name=data.name,
        unit=data.unit,
        baseline_value=data.baseline_value,
        baseline_date=data.baseline_date,
        target_value=data.target_value,
    )
    await AuditRepository(db).log(
        user_id=actor.id,
        action="impact_indicator.create",
        entity_type="impact_indicator",
        entity_id=indicator.id,
        meta={"project_id": str(project_id)},
    )
    await db.commit()
    return indicator


async def update_endline(
    db: AsyncSession,
    project_id: uuid.UUID,
    indicator_id: uuid.UUID,
    *,
    data: ImpactIndicatorEndlineUpdate,
    actor: User,
) -> ImpactIndicator:
    """Claimed impact — not verified. See verify_indicator for the separate
    verification step; a project reaching COMPLETED never implies this."""
    await _authorize_project(db, project_id, actor)
    indicator_repo = ImpactIndicatorRepository(db)
    indicator = await indicator_repo.get(indicator_id)
    if indicator is None or indicator.project_id != project_id:
        raise INDICATOR_NOT_FOUND

    indicator.actual_value = data.actual_value
    indicator.endline_date = data.endline_date
    indicator.endline_evidence = data.endline_evidence
    # A new endline claim invalidates any prior verification.
    indicator.verified_at = None
    indicator.verified_by_id = None

    await AuditRepository(db).log(
        user_id=actor.id, action="impact_indicator.endline_claimed", entity_type="impact_indicator", entity_id=indicator.id
    )
    await db.commit()
    await db.refresh(indicator)
    return indicator


async def verify_indicator(
    db: AsyncSession, project_id: uuid.UUID, indicator_id: uuid.UUID, *, approve: bool, actor: User
) -> ImpactIndicator:
    if actor.role not in (Role.VALIDATOR, Role.SUPERADMIN):
        raise VERIFICATION_REQUIRES_VALIDATOR
    indicator_repo = ImpactIndicatorRepository(db)
    indicator = await indicator_repo.get(indicator_id)
    if indicator is None or indicator.project_id != project_id:
        raise INDICATOR_NOT_FOUND
    if indicator.actual_value is None:
        raise ENDLINE_NOT_SET

    if approve:
        indicator.verified_at = datetime.now(timezone.utc)
        indicator.verified_by_id = actor.id
    else:
        indicator.verified_at = None
        indicator.verified_by_id = None

    await AuditRepository(db).log(
        user_id=actor.id,
        action="impact_indicator.verified" if approve else "impact_indicator.verification_rejected",
        entity_type="impact_indicator",
        entity_id=indicator.id,
    )
    await db.commit()
    await db.refresh(indicator)
    return indicator
