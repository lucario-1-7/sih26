import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import require_role
from app.db.session import get_db
from app.models.enums import ProjectStatus, Role
from app.models.user import User
from app.schemas.deliverable import DeliverableCreate, DeliverableResponse, DeliverableUpdate, DeliverableVerify
from app.schemas.impact_indicator import (
    ImpactIndicatorCreate,
    ImpactIndicatorEndlineUpdate,
    ImpactIndicatorResponse,
    ImpactIndicatorVerify,
)
from app.schemas.milestone import MilestoneCreate, MilestoneResponse, MilestoneUpdate
from app.schemas.pagination import PaginatedResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.project_participant import (
    ProjectParticipantCreate,
    ProjectParticipantResponse,
    ProjectParticipantUpdate,
)
from app.services import (
    deliverable_service,
    impact_indicator_service,
    milestone_service,
    project_participant_service,
    project_service,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED, summary="Create a project"
)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.COORDINATOR, Role.SUPERADMIN)),
) -> ProjectResponse:
    project = await project_service.create_project(db, data=payload, actor=user)
    return await project_service.to_response(db, project)


@router.get("", response_model=PaginatedResponse[ProjectResponse], summary="List projects")
async def list_projects(
    cluster_id: uuid.UUID | None = None,
    status_filter: ProjectStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ProjectResponse]:
    projects, next_cursor = await project_service.list_projects(
        db, cluster_id=cluster_id, status_filter=status_filter, limit=limit, cursor=cursor
    )
    return PaginatedResponse(
        items=await project_service.to_responses(db, projects),
        next_cursor=next_cursor,
    )


@router.get("/{project_id}", response_model=ProjectResponse, summary="Get a project by id")
async def get_project(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ProjectResponse:
    project = await project_service.get_project(db, project_id)
    return await project_service.to_response(db, project)


@router.patch("/{project_id}", response_model=ProjectResponse, summary="Update a project")
async def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.COORDINATOR, Role.FACULTY, Role.SUPERADMIN)),
) -> ProjectResponse:
    project = await project_service.update_project(db, project_id, data=payload, actor=user)
    return await project_service.to_response(db, project)


# --- Project participants (students — no user account, faculty/coordinator managed) ---


@router.get(
    "/{project_id}/participants",
    response_model=PaginatedResponse[ProjectParticipantResponse],
    summary="List a project's student/participant records (Faculty/Coordinator of that institution, or Superadmin)",
)
async def list_project_participants(
    project_id: uuid.UUID,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.FACULTY, Role.COORDINATOR, Role.SUPERADMIN)),
) -> PaginatedResponse[ProjectParticipantResponse]:
    participants, next_cursor = await project_participant_service.list_participants(
        db, project_id, actor=user, limit=limit, cursor=cursor
    )
    return PaginatedResponse(
        items=[ProjectParticipantResponse.model_validate(p) for p in participants],
        next_cursor=next_cursor,
    )


@router.post(
    "/{project_id}/participants",
    response_model=ProjectParticipantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a student/participant record to a project (no login is created for them)",
)
async def create_project_participant(
    project_id: uuid.UUID,
    payload: ProjectParticipantCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.FACULTY, Role.COORDINATOR, Role.SUPERADMIN)),
) -> ProjectParticipantResponse:
    participant = await project_participant_service.create_participant(
        db, project_id, data=payload, actor=user
    )
    return ProjectParticipantResponse.model_validate(participant)


@router.patch(
    "/{project_id}/participants/{participant_id}",
    response_model=ProjectParticipantResponse,
    summary="Update a project participant record",
)
async def update_project_participant(
    project_id: uuid.UUID,
    participant_id: uuid.UUID,
    payload: ProjectParticipantUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.FACULTY, Role.COORDINATOR, Role.SUPERADMIN)),
) -> ProjectParticipantResponse:
    participant = await project_participant_service.update_participant(
        db, project_id, participant_id, data=payload, actor=user
    )
    return ProjectParticipantResponse.model_validate(participant)


# --- Milestones ---


@router.get(
    "/{project_id}/milestones",
    response_model=PaginatedResponse[MilestoneResponse],
    summary="List a project's milestones",
)
async def list_milestones(
    project_id: uuid.UUID,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.FACULTY, Role.COORDINATOR, Role.SUPERADMIN)),
) -> PaginatedResponse[MilestoneResponse]:
    milestones, next_cursor = await milestone_service.list_milestones(
        db, project_id, actor=user, limit=limit, cursor=cursor
    )
    return PaginatedResponse(
        items=[MilestoneResponse.model_validate(m) for m in milestones], next_cursor=next_cursor
    )


@router.post(
    "/{project_id}/milestones",
    response_model=MilestoneResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project milestone",
)
async def create_milestone(
    project_id: uuid.UUID,
    payload: MilestoneCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.FACULTY, Role.COORDINATOR, Role.SUPERADMIN)),
) -> MilestoneResponse:
    milestone = await milestone_service.create_milestone(db, project_id, data=payload, actor=user)
    return MilestoneResponse.model_validate(milestone)


@router.patch(
    "/{project_id}/milestones/{milestone_id}",
    response_model=MilestoneResponse,
    summary="Update a milestone, including marking it complete",
)
async def update_milestone(
    project_id: uuid.UUID,
    milestone_id: uuid.UUID,
    payload: MilestoneUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.FACULTY, Role.COORDINATOR, Role.SUPERADMIN)),
) -> MilestoneResponse:
    milestone = await milestone_service.update_milestone(
        db, project_id, milestone_id, data=payload, actor=user
    )
    return MilestoneResponse.model_validate(milestone)


# --- Deliverables ---


@router.get(
    "/{project_id}/deliverables",
    response_model=PaginatedResponse[DeliverableResponse],
    summary="List a project's deliverables",
)
async def list_deliverables(
    project_id: uuid.UUID,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.FACULTY, Role.COORDINATOR, Role.SUPERADMIN)),
) -> PaginatedResponse[DeliverableResponse]:
    deliverables, next_cursor = await deliverable_service.list_deliverables(
        db, project_id, actor=user, limit=limit, cursor=cursor
    )
    return PaginatedResponse(
        items=[DeliverableResponse.model_validate(d) for d in deliverables], next_cursor=next_cursor
    )


@router.post(
    "/{project_id}/deliverables",
    response_model=DeliverableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project deliverable",
)
async def create_deliverable(
    project_id: uuid.UUID,
    payload: DeliverableCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.FACULTY, Role.COORDINATOR, Role.SUPERADMIN)),
) -> DeliverableResponse:
    deliverable = await deliverable_service.create_deliverable(db, project_id, data=payload, actor=user)
    return DeliverableResponse.model_validate(deliverable)


@router.patch(
    "/{project_id}/deliverables/{deliverable_id}",
    response_model=DeliverableResponse,
    summary="Update a deliverable / submit evidence (Faculty)",
)
async def update_deliverable(
    project_id: uuid.UUID,
    deliverable_id: uuid.UUID,
    payload: DeliverableUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.FACULTY, Role.COORDINATOR, Role.SUPERADMIN)),
) -> DeliverableResponse:
    deliverable = await deliverable_service.update_deliverable(
        db, project_id, deliverable_id, data=payload, actor=user
    )
    return DeliverableResponse.model_validate(deliverable)


@router.post(
    "/{project_id}/deliverables/{deliverable_id}/verify",
    response_model=DeliverableResponse,
    summary="Verify or reject a submitted deliverable (Coordinator/Superadmin)",
)
async def verify_deliverable(
    project_id: uuid.UUID,
    deliverable_id: uuid.UUID,
    payload: DeliverableVerify,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.COORDINATOR, Role.SUPERADMIN)),
) -> DeliverableResponse:
    deliverable = await deliverable_service.verify_deliverable(
        db, project_id, deliverable_id, approve=payload.approve, actor=user
    )
    return DeliverableResponse.model_validate(deliverable)


# --- Impact indicators ---


@router.get(
    "/{project_id}/impact-indicators",
    response_model=PaginatedResponse[ImpactIndicatorResponse],
    summary="List a project's impact indicators",
)
async def list_impact_indicators(
    project_id: uuid.UUID,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.FACULTY, Role.COORDINATOR, Role.VALIDATOR, Role.SUPERADMIN)),
) -> PaginatedResponse[ImpactIndicatorResponse]:
    indicators, next_cursor = await impact_indicator_service.list_indicators(
        db, project_id, actor=user, limit=limit, cursor=cursor
    )
    return PaginatedResponse(
        items=[ImpactIndicatorResponse.model_validate(i) for i in indicators], next_cursor=next_cursor
    )


@router.post(
    "/{project_id}/impact-indicators",
    response_model=ImpactIndicatorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Declare an impact indicator with its baseline (before implementation)",
)
async def create_impact_indicator(
    project_id: uuid.UUID,
    payload: ImpactIndicatorCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.FACULTY, Role.COORDINATOR, Role.SUPERADMIN)),
) -> ImpactIndicatorResponse:
    indicator = await impact_indicator_service.create_indicator(db, project_id, data=payload, actor=user)
    return ImpactIndicatorResponse.model_validate(indicator)


@router.patch(
    "/{project_id}/impact-indicators/{indicator_id}/endline",
    response_model=ImpactIndicatorResponse,
    summary="Submit the claimed (unverified) endline value",
)
async def update_impact_indicator_endline(
    project_id: uuid.UUID,
    indicator_id: uuid.UUID,
    payload: ImpactIndicatorEndlineUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.FACULTY, Role.COORDINATOR, Role.SUPERADMIN)),
) -> ImpactIndicatorResponse:
    indicator = await impact_indicator_service.update_endline(
        db, project_id, indicator_id, data=payload, actor=user
    )
    return ImpactIndicatorResponse.model_validate(indicator)


@router.post(
    "/{project_id}/impact-indicators/{indicator_id}/verify",
    response_model=ImpactIndicatorResponse,
    summary="Independently verify (or reject) claimed impact (Validator/Superadmin)",
)
async def verify_impact_indicator(
    project_id: uuid.UUID,
    indicator_id: uuid.UUID,
    payload: ImpactIndicatorVerify,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.VALIDATOR, Role.SUPERADMIN)),
) -> ImpactIndicatorResponse:
    indicator = await impact_indicator_service.verify_indicator(
        db, project_id, indicator_id, approve=payload.approve, actor=user
    )
    return ImpactIndicatorResponse.model_validate(indicator)
