import httpx
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.redis import get_redis
from app.db.session import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Liveness/readiness check for server, database, redis, and ML service")
async def health(db: AsyncSession = Depends(get_db)) -> dict:
    settings = get_settings()

    db_ok = True
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    redis_ok = True
    try:
        await get_redis().ping()
    except Exception:
        redis_ok = False

    ml_ok = True
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{settings.ML_SERVICE_URL}/health")
            ml_ok = resp.status_code == 200
    except Exception:
        ml_ok = False

    status = "ok" if (db_ok and redis_ok and ml_ok) else "degraded"
    return {
        "status": status,
        "database": "ok" if db_ok else "unavailable",
        "redis": "ok" if redis_ok else "unavailable",
        "ml_service": "ok" if ml_ok else "unavailable",
    }
