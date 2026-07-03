"""Скрипт импорта данных из CSV в PostgreSQL и Elasticsearch."""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from core.config import settings
from core.database import AsyncSession, Base, engine
from core.logger import logger
from models.post import Post
from parser import get_csv_data
from schemas.post import PostData

CSV_FILE = Path(__file__).parent.parent / "posts.csv"
ES_INDEX = "posts"


def parse_rubrics(raw: str) -> list[str]:
    """Парсит поле rubrics из CSV (JSON-строка или список через запятую)."""
    if not raw or raw == "[]":
        return []
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return [r.strip() for r in raw.split(",") if r.strip()]


def parse_date(raw: str) -> datetime:
    """Парсит дату из CSV."""
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


async def create_tables() -> None:
    """Создает таблицы в PostgreSQL."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Таблицы PostgreSQL созданы")


async def create_index(es: AsyncElasticsearch) -> None:
    """Создает индекс Elasticsearch."""
    try:
        await es.indices.delete(index=ES_INDEX)
        logger.info(f"Старый индекс '{ES_INDEX}' удалён")
    except Exception as e:
        logger.info(f"Индекс '{ES_INDEX}' не существовал или ошибка удаления: {e}")

    await es.indices.create(
        index=ES_INDEX,
        mappings={
            "properties": {
                "id": {"type": "integer"},
                "text": {"type": "text", "analyzer": "standard"},
            }
        },
    )
    logger.info(f"Индекс '{ES_INDEX}' создан")


async def import_to_postgres(data: list[dict]) -> list[PostData]:
    """Импортирует данные в PostgreSQL и возвращает список PostData."""
    async with AsyncSession() as session:
        posts_data = []
        for idx, row in enumerate(data, start=1):
            post_data = PostData(
                id=idx,
                text=row.get("text", ""),
                rubrics=parse_rubrics(row.get("rubrics", "[]")),
                created_date=parse_date(row["created_date"]),
            )
            posts_data.append(post_data)

            post = Post(
                id=post_data.id,
                text=post_data.text,
                rubrics=post_data.rubrics,
                created_date=post_data.created_date,
            )
            session.add(post)

        await session.commit()

    logger.info(f"В PostgreSQL импортировано {len(posts_data)} записей")
    return posts_data


async def import_to_elasticsearch(posts: list[PostData]) -> None:
    """Импортирует данные в Elasticsearch через helpers.async_bulk."""
    es = AsyncElasticsearch(hosts=[settings.ELASTICSEARCH_URL])
    try:
        actions = (
            {
                "_index": ES_INDEX,
                "_id": post.id,
                "_source": {"id": post.id, "text": post.text},
            }
            for post in posts
        )
        success, errors = await async_bulk(es, actions)
        if errors:
            logger.error(f"Ошибки индексации: {errors}")
        else:
            logger.info(f"В Elasticsearch проиндексировано {success} документов")
    finally:
        await es.close()


async def main():
    """Основная функция импорта."""
    data = list(get_csv_data(str(CSV_FILE)))
    logger.info(f"Прочитано {len(data)} записей из CSV")

    # создаём таблицу в бд
    await create_tables()

    # импортируем данные в бд
    posts = await import_to_postgres(data)

    # создаём индекс в эластике
    es = AsyncElasticsearch(hosts=[settings.ELASTICSEARCH_URL])
    try:
        await create_index(es)
    finally:
        await es.close()

    # импортируем данные в эластик
    await import_to_elasticsearch(posts)

    logger.info("Импорт завершен")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
