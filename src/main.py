import json
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from core.database import Base, engine
from router import router as posts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    openapi_schema = app.openapi()
    with open("docs.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)

    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(posts_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
