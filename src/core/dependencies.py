from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSession as async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронный генератор сессии"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
