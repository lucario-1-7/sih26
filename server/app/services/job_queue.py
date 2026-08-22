from arq import ArqRedis, create_pool
from arq.connections import RedisSettings

from app.core.config import get_settings


async def get_arq_pool() -> ArqRedis:
    """A fresh pool per call — avoids binding a cached connection to whichever
    event loop happened to create it first (see app.db.redis.get_redis)."""
    return await create_pool(RedisSettings.from_dsn(get_settings().REDIS_URL))


async def enqueue_duplicate_candidate_generation(challenge_id: str) -> None:
    pool = await get_arq_pool()
    await pool.enqueue_job("generate_duplicate_candidates", challenge_id)


async def enqueue_consortium_suggestion(project_id: str, team_size: int) -> None:
    pool = await get_arq_pool()
    await pool.enqueue_job("generate_consortium_suggestion", project_id, team_size)


async def enqueue_cluster_embedding_generation(cluster_id: str) -> None:
    pool = await get_arq_pool()
    await pool.enqueue_job("generate_cluster_embedding", cluster_id)
