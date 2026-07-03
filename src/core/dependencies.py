from typing import AsyncGenerator

from elasticsearch import AsyncElasticsearch
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import AsyncSession as async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_es() -> AsyncGenerator[AsyncElasticsearch, None]:
    es = AsyncElasticsearch(hosts=[settings.ELASTICSEARCH_URL])
    try:
        yield es
    finally:
        await es.close()
