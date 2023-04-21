from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.api.v1 import api
from app.core import logging_config  # noqa: F401
from app.db.session import init_db, stop_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await init_db()

    yield

    await stop_db()


app = FastAPI(
    docs_url="/openapi",
    openapi_url="/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


app.include_router(api.api_router, prefix="/api/v1")


if __name__ == "__main__":
    # для локального запуска и дебаггера
    local_port = 8080
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # noqa: S104
        port=local_port,
        reload=True,
    )
