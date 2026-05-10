from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

engine = create_async_engine(settings.POSTGRES_DSN, echo=False, pool_size=10)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

sync_engine = create_engine(settings.POSTGRES_DSN.replace("+asyncpg", "+psycopg2"), echo=False, pool_size=10)
sync_session = sessionmaker(sync_engine, class_=Session, expire_on_commit=False)


async def get_session():
    async with async_session() as session:
        yield session
