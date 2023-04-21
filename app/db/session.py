import logging
import socket

import asyncpg
import backoff
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.db_pre_start import create_admin, insert_roles, recreate_tables

# нужно импортировать модели, чтобы алхимия знала о них
from app.models.models import Permission, Role, User  # noqa: F401

engine = create_async_engine(
    settings.sqlalchemy_database_uri,
    echo=settings.debug,
)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

logger = logging.getLogger(__name__)


@backoff.on_exception(
    backoff.expo,
    exception=(
        ConnectionRefusedError,
        asyncpg.CannotConnectNowError,
        socket.gaierror,
    ),
    max_time=60,
    max_value=5,
)
async def check_connection() -> None:
    async with engine.connect() as async_conn:
        await async_conn.execute(text("SELECT 1"))


async def init_db() -> None:
    await check_connection()
    async with async_session() as session:
        # пересоздаем таблицы при каждом рестарте, пока нет миграций
        await recreate_tables(session)
        await insert_roles(session)
        await create_admin(session)


async def stop_db() -> None:
    await engine.dispose()
