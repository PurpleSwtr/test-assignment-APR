from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select

from core.config import settings
from core.database import AsyncSession
from core.dependencies import get_db, get_es
from core.logger import logger
from models.post import Post

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/search")
async def search(
    query: str,
    db: AsyncSession = Depends(get_db),
    es: AsyncElasticsearch = Depends(get_es),
) -> list[dict]:
    """Поиск документов по текстовому запросу.
    возвращает первые 20 документов из PostgreSQL, упорядоченных по дате создания.

    Args:
        query: Текстовый запрос для поиска.
        db: Асинхронная сессия PostgreSQL.
        es: Асинхронный клиент Elasticsearch.

    Returns:
        Список из максимум 20 документов со всеми полями БД
        (id, rubrics, text, created_date).
    """
    response = await es.search(
        index=settings.ES_INDEX,
        query={"match": {"text": query}},
        size=20,
    )

    hits = response.get("hits", {}).get("hits", [])
    if not hits:
        return []

    post_ids = [int(hit["_id"]) for hit in hits]

    stmt = (
        select(Post)
        .where(Post.id.in_(post_ids))
        .order_by(Post.created_date.desc())
        .limit(20)
    )
    result = await db.execute(stmt)
    posts = result.scalars().all()

    return [
        {
            "id": post.id,
            "rubrics": post.rubrics,
            "text": post.text,
            "created_date": post.created_date.isoformat(),
        }
        for post in posts
    ]


@router.delete("/delete_post/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    es: AsyncElasticsearch = Depends(get_es),
) -> dict[str, str]:
    """Удаление поста по его ID.
    Удаляет запись как из базы данных PostgreSQL, так и из индекса Elasticsearch.

    Args:
        post_id: Уникальный идентификатор поста.
        db: Асинхронная сессия PostgreSQL.
        es: Асинхронный клиент Elasticsearch.

    Returns:
        {"status": "success"} при успешном удалении.

    Raises:
        HTTPException(404): Если документ с указанным ID не найден.
    """
    stmt = select(Post).where(Post.id == post_id)
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пост {post_id} не найден",
        )

    await db.execute(delete(Post).where(Post.id == post_id))
    await db.commit()

    try:
        await es.delete(index=settings.ES_INDEX, id=str(post_id))
    except Exception as e:
        logger.error(f"Не удалось удалить пост {post_id} из ES: {e}")

    return {"status": "success"}
