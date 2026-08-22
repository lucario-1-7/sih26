import uuid

from app.core.config import get_settings
from app.db.redis import get_redis


def _key(user_id: uuid.UUID, jti: str) -> str:
    return f"refresh:{user_id}:{jti}"


async def store_refresh_jti(user_id: uuid.UUID, jti: str) -> None:
    settings = get_settings()
    await get_redis().set(_key(user_id, jti), "1", ex=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60)


async def is_refresh_jti_valid(user_id: uuid.UUID, jti: str) -> bool:
    return await get_redis().exists(_key(user_id, jti)) == 1


async def revoke_refresh_jti(user_id: uuid.UUID, jti: str) -> None:
    await get_redis().delete(_key(user_id, jti))
