import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.solution import Solution
from app.repositories.audit_repository import AuditRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.solution_repository import SolutionRepository
from app.schemas.solution import SolutionCreate

NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"detail": "Solution not found", "code": "NOT_FOUND"}
)
PROJECT_NOT_FOUND = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail={"detail": "project_id does not reference an existing project", "code": "INVALID_PROJECT"},
)


async def create_solution(db: AsyncSession, *, data: SolutionCreate, actor_id: uuid.UUID) -> Solution:
    project = await ProjectRepository(db).get(data.project_id)
    if project is None:
        raise PROJECT_NOT_FOUND
    solution = await SolutionRepository(db).create(
        project_id=data.project_id, title=data.title, description=data.description
    )
    await AuditRepository(db).log(
        user_id=actor_id, action="solution.create", entity_type="solution", entity_id=solution.id
    )
    await db.commit()
    return solution


async def get_solution(db: AsyncSession, solution_id: uuid.UUID) -> Solution:
    solution = await SolutionRepository(db).get(solution_id)
    if solution is None:
        raise NOT_FOUND
    return solution


async def list_solutions(
    db: AsyncSession, *, project_id: uuid.UUID | None, limit: int, offset: int
) -> list[Solution]:
    return await SolutionRepository(db).list(project_id=project_id, limit=limit, offset=offset)
