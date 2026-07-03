from fastapi import APIRouter, Depends

from core.database import AsyncSession
from core.dependencies import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/search")
async def search(query: str, db: AsyncSession = Depends(get_db)): ...


@router.delete("/delete_post/{post_id}")
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)): ...
