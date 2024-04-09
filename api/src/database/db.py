from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from config import config

engine = create_async_engine(
    config.db_url,
    future=True,
    echo=False,
    pool_pre_ping=True
)


class Base(DeclarativeBase):
    pass


async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
