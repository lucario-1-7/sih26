from fastapi import APIRouter

from app.api.v1.administrative_areas.routes import router as administrative_areas_router
from app.api.v1.analytics.routes import router as analytics_router
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.challenges.routes import router as challenges_router
from app.api.v1.clusters.routes import router as clusters_router
from app.api.v1.collaboration.routes import router as collaboration_router
from app.api.v1.duplicate.routes import router as duplicate_router
from app.api.v1.health.routes import router as health_router
from app.api.v1.matching.routes import router as matching_router
from app.api.v1.projects.routes import router as projects_router
from app.api.v1.solutions.routes import router as solutions_router
from app.api.v1.themes.routes import router as themes_router
from app.api.v1.users.routes import router as users_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(administrative_areas_router)
api_router.include_router(challenges_router)
api_router.include_router(clusters_router)
api_router.include_router(themes_router)
api_router.include_router(projects_router)
api_router.include_router(solutions_router)
api_router.include_router(duplicate_router)
api_router.include_router(matching_router)
api_router.include_router(collaboration_router)
api_router.include_router(analytics_router)
