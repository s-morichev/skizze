import asyncio
from pathlib import Path
from typing import AsyncGenerator, Iterator

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# Для запуска тестов на хосте явно загружаем переменные окружения
# из .env.test в корневой папке до импорта приложения, так как pytest
# сам по умолчанию загружает переменные окружения из .env
# TODO настроить тестирование в докере
base_dir = Path(__file__).parent.parent.parent
env_test = base_dir / ".env.test"
load_dotenv(env_test, override=True)

from app.db.db_pre_start import insert_roles, recreate_tables  # noqa: E402
from app.db.session import async_session  # noqa: E402
from app.main import app  # noqa: E402
from app.tests.authentication import authenticate_user  # noqa: E402
from app.tests.constants import (  # noqa: E402
    EMAIL_TEST_USER,
    PASSWORD_TEST_USER,
)


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as test_session:
        yield test_session


@pytest_asyncio.fixture(scope="module")
async def client(session: AsyncSession) -> AsyncClient:
    await recreate_tables(session)
    await insert_roles(session)
    return AsyncClient(app=app, base_url="http://localhost:8000")


@pytest_asyncio.fixture(scope="module")
async def user_token_headers(
    client: AsyncClient, session: AsyncSession
) -> dict[str, str]:
    return await authenticate_user(
        client=client,
        session=session,
        email=EMAIL_TEST_USER,
        password=PASSWORD_TEST_USER,
    )
