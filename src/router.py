from fastapi import APIRouter, Depends

from core.database import AsyncSession
from core.dependencies import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/search")
async def search(query: str, db: AsyncSession = Depends(get_db)) -> list[dict]:
    """Поиск документов по текстовому запросу.
    возвращает первые 20 документов из PostgreSQL, упорядоченных по дате создания.

    Args:
        query (str): Текстовый запрос для поиска.
        db (AsyncSession, optional): Асинхронная сессия базы данных.
            Автоматически внедряется через Depends(get_db).

    Returns:
        list[dict]: Список из максимум 20 документов со всеми полями БД
            (id, rubrics, text, created_date), отсортированных по created_date
            в порядке убывания.
    """


@router.delete("/delete_post/{post_id}")
async def delete_post(
    post_id: int, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """Удаление поста по его ID.
    Удаляет запись как из базы данных PostgreSQL, так и из индекса Elasticsearch.

    Args:
        post_id (int): Уникальный идентификатор поста для удаления.
        db (AsyncSession, optional): Асинхронная сессия базы данных.
            Автоматически внедряется через Depends(get_db).

    Returns:
        dict: Словарь с результатом операции:
            {"status": "success"}

    Raises:
        HTTPException: Если документ с указанным ID не найден (404).
    """
