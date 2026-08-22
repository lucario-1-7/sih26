import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import Role, SolutionStatus
from app.models.solution import Solution
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.solution_repository import SolutionRepository
from app.schemas.solution import ReplicationCandidateResponse, SolutionCreate, SolutionUpdate
from app.services import ml_client

NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Solution not found", "code": "NOT_FOUND"}
)
PROJECT_NOT_FOUND = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail={"detail": "project_id does not reference an existing project", "code": "INVALID_PROJECT"},
)
CROSS_ORGANIZATION_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail={"detail": "Cannot manage another institution's project outcome", "code": "FORBIDDEN"},
)
REPLICATION_REQUIRES_EMBEDDING = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail={"detail": "Solution has no embedding yet", "code": "CONFLICT"},
)
REPLICATION_CANDIDATE_LIMIT = 10


async def create_solution(db: AsyncSession, *, data: SolutionCreate, actor: User) -> Solution:
    project = await ProjectRepository(db).get(data.project_id)
    if project is None:
        raise PROJECT_NOT_FOUND
    if actor.role != Role.SUPERADMIN and project.organization_id != actor.organization_id:
        raise CROSS_ORGANIZATION_FORBIDDEN

    # Computed synchronously — solutions are created infrequently (once per
    # completed project), unlike the high-volume challenge/cluster paths
    # that use a background job instead.
    embedding = await ml_client.embed_text(f"{data.title}\n{data.description or ''}\n{data.outcome or ''}")

    solution = await SolutionRepository(db).create(
        project_id=data.project_id,
        title=data.title,
        description=data.description,
        outcome=data.outcome,
        embedding=embedding,
    )
    await AuditRepository(db).log(
        user_id=actor.id, action="solution.create", entity_type="solution", entity_id=solution.id
    )
    await db.commit()
    return solution


async def get_solution(db: AsyncSession, solution_id: uuid.UUID) -> Solution:
    solution = await SolutionRepository(db).get(solution_id)
    if solution is None:
        raise NOT_FOUND
    return solution


async def list_solutions(
    db: AsyncSession, *, project_id: uuid.UUID | None, limit: int, cursor: str | None
) -> tuple[list[Solution], str | None]:
    return await SolutionRepository(db).list(project_id=project_id, limit=limit, cursor=cursor)


async def update_solution(db: AsyncSession, solution_id: uuid.UUID, *, data: SolutionUpdate, actor: User) -> Solution:
    solution_repo = SolutionRepository(db)
    solution = await solution_repo.get(solution_id)
    if solution is None:
        raise NOT_FOUND
    project = await ProjectRepository(db).get(solution.project_id)
    if actor.role != Role.SUPERADMIN and (project is None or project.organization_id != actor.organization_id):
        raise CROSS_ORGANIZATION_FORBIDDEN

    if data.title is not None:
        solution.title = data.title
    if data.description is not None:
        solution.description = data.description
    if data.outcome is not None:
        solution.outcome = data.outcome
    if data.status is not None:
        solution.status = data.status

    await AuditRepository(db).log(
        user_id=actor.id,
        action="solution.published" if data.status == SolutionStatus.PUBLISHED else "solution.update",
        entity_type="solution",
        entity_id=solution.id,
    )
    await db.commit()
    await db.refresh(solution)
    return solution


async def get_replication_candidates(db: AsyncSession, solution_id: uuid.UUID) -> list[ReplicationCandidateResponse]:
    """Read-only recommendation: ranked ACTIVE clusters (with no project yet)
    that this solution's embedding is nearest to. Nothing here creates a
    project or links anything — replication requires a human (Coordinator)
    to actually propose a project against a suggested cluster."""
    solution = await SolutionRepository(db).get(solution_id)
    if solution is None:
        raise NOT_FOUND
    if solution.embedding is None:
        raise REPLICATION_REQUIRES_EMBEDDING

    pairs = await ClusterRepository(db).find_open_nearest_by_embedding(
        embedding=solution.embedding, limit=REPLICATION_CANDIDATE_LIMIT
    )
    return [
        ReplicationCandidateResponse(
            cluster_id=cluster.id, cluster_title=cluster.title, similarity=max(0.0, 1.0 - distance)
        )
        for cluster, distance in pairs
    ]
