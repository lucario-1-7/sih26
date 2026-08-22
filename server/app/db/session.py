from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

# NullPool: a fresh connection per checkout, closed on checkin. This avoids
# asyncpg connections outliving the event loop that created them, which
# otherwise breaks under Windows' ProactorEventLoop with per-test event loops
# (pytest-asyncio) and under ARQ's separate worker event loop. Simpler and
# more portable than pinning connection reuse to loop lifecycle; revisit if
# connection-setup latency becomes a measured bottleneck.
engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool, future=True)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
