from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .models.base import Base
from tgbot.config import DbConfig


async def create_engine(db: DbConfig, echo: bool = False) -> AsyncEngine:
    engine = create_async_engine(
        db.construct_sqlalchemy_url(),
        query_cache_size=1200,
        pool_size=20,
        max_overflow=200,
        future=True,
        echo=echo,
    )

    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return engine


def create_session_pool(engine: AsyncEngine):
    session_pool = async_sessionmaker(bind=engine, expire_on_commit=False)
    return session_pool
