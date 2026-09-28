from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from config.settings import DATABASE_URL

# For ASYNC
async_engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# For synchronous
sync_engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionSync = sessionmaker(sync_engine, expire_on_commit=False)


async def get_session():
    async with SessionLocal() as session:
        yield session