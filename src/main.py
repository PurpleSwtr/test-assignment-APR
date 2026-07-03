import json
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_engine = engine
    Base.metadata.create_all(bind=engine)
    yield
    app.state.db_engine.dispose()


app = FastAPI(lifespan=lifespan)

openapi_schema = app.openapi()

with open("docs.json", "w") as f:
    json.dump(openapi_schema, f, indent=2)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
