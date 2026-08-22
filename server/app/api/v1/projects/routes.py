import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import require_role
from app.db.session import get_db
from app.models.enums import ProjectStatus, Role
from app.models.user import User
from app.schemas.pagination import PaginatedResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED, summary="Create a project"
)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.OFFICER, Role.ADMIN)),
) -> ProjectResponse:
    project = await project_service.create_project(db, data=payload, actor_id=user.id)
    return ProjectResponse.model_validate(project)


@router.get("", response_model=PaginatedResponse[ProjectResponse], summary="List projects")
async def list_projects(
    cluster_id: uuid.UUID | None = None,
    status_filter: ProjectStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ProjectResponse]:
    projects = await project_service.list_projects(
        db, cluster_id=cluster_id, status_filter=status_filter, limit=limit, offset=offset
    )
    return PaginatedResponse(
        items=[ProjectResponse.model_validate(p) for p in projects],
        next_cursor=str(offset + limit) if len(projects) == limit else None,
    )


@router.get("/{project_id}", response_model=ProjectResponse, summary="Get a project by id")
async def get_project(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ProjectResponse:
    project = await project_service.get_project(db, project_id)
    return ProjectResponse.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectResponse, summary="Update a project")
async def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(Role.OFFICER, Role.ADMIN)),
) -> ProjectResponse:
    project = await project_service.update_project(db, project_id, data=payload, actor_id=user.id)
    return ProjectResponse.model_validate(project)
