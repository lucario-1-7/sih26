from arq.connections import RedisSettings

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.workers.tasks import (
    generate_cluster_embedding,
    generate_consortium_suggestion,
    generate_duplicate_candidates,
)


class WorkerSettings:
    functions = [generate_duplicate_candidates, generate_consortium_suggestion, generate_cluster_embedding]
    redis_settings = RedisSettings.from_dsn(get_settings().REDIS_URL)
    max_tries = 3
    job_timeout = 120
    # Serialized on purpose: two duplicate-candidate jobs running concurrently
    # can race (job B's neighbor search can run before job A's embedding
    # commits), which would silently miss a real duplicate. At this project's
    # expected submission volume, trading worker throughput for correctness
    # here is the right call — revisit if queue depth becomes a bottleneck.
    max_jobs = 1

    @staticmethod
    async def on_startup(ctx):
        configure_logging()
