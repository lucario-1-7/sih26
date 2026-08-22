from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import require_role
from app.db.session import get_db
from app.models.enums import Role
from app.models.user import User
from app.schemas.analytics import ChallengeAnalytics, IndustryAnalytics, MLAnalytics, ModelInfo, ProjectAnalytics
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])

_SUPERADMIN_ONLY = Depends(require_role(Role.SUPERADMIN))


@router.get("/challenges", response_model=ChallengeAnalytics, summary="Platform-wide challenge statistics")
async def challenge_analytics(
    db: AsyncSession = Depends(get_db), _user: User = _SUPERADMIN_ONLY
) -> ChallengeAnalytics:
    return await analytics_service.get_challenge_analytics(db)


@router.get("/projects", response_model=ProjectAnalytics, summary="Platform-wide project statistics")
async def project_analytics(db: AsyncSession = Depends(get_db), _user: User = _SUPERADMIN_ONLY) -> ProjectAnalytics:
    return await analytics_service.get_project_analytics(db)


@router.get("/industry", response_model=IndustryAnalytics, summary="Industry collaboration/funding statistics")
async def industry_analytics(
    db: AsyncSession = Depends(get_db), _user: User = _SUPERADMIN_ONLY
) -> IndustryAnalytics:
    return await analytics_service.get_industry_analytics(db)


@router.get("/ml", response_model=MLAnalytics, summary="ML/embedding/duplicate-detection statistics")
async def ml_analytics(db: AsyncSession = Depends(get_db), _user: User = _SUPERADMIN_ONLY) -> MLAnalytics:
    return await analytics_service.get_ml_analytics(db)


@router.get("/model-info", response_model=ModelInfo, summary="ML model metadata (name, version, config)")
async def model_info(_user: User = _SUPERADMIN_ONLY) -> ModelInfo:
    return analytics_service.get_model_info()
