"""
Database utilities for Lexi bot
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.settings import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, echo=settings.debug)
session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession]:
    """Get async database session"""
    async with session_maker() as session:
        yield session
