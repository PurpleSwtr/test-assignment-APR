from fastapi import APIRouter

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/search")
async def search(): ...


@router.delete("/delete_post")
async def delete_post(): ...
