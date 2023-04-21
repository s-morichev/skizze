from datetime import timedelta
from http import HTTPStatus

import pytest
import pytest_asyncio
from freezegun import freeze_time
from httpx import AsyncClient

from app.core.config import settings
from app.tests.constants import (
    EMAIL_TEST_USER,
    PASSWORD_FIELD,
    PASSWORD_TEST_USER,
    USERNAME_FIELD,
)

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="module")
async def valid_access_token(user_token_headers: dict[str, str]) -> str:
    header = user_token_headers["Authorization"]
    return header[len("Bearer ") :]


@pytest_asyncio.fixture(scope="module")
async def invalid_access_token(valid_access_token: str) -> str:
    token_head = valid_access_token[:-1]
    if valid_access_token[-1] == "a":
        token = f"{token_head}b"
    else:
        token = f"{token_head}a"
    return token


async def test_login(
    client: AsyncClient, user_token_headers: dict[str, str]
) -> None:
    response = await client.post(
        "api/v1/login",
        data={
            USERNAME_FIELD: EMAIL_TEST_USER,
            PASSWORD_FIELD: PASSWORD_TEST_USER,
        },
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert "access_token" in token and "token_type" in token
    assert token["access_token"]
    assert token["token_type"] == "bearer"


@pytest.mark.parametrize(
    "update_user_data, status_code",
    [
        (
            {
                USERNAME_FIELD: EMAIL_TEST_USER,
                PASSWORD_FIELD: f"bad{PASSWORD_TEST_USER}",
            },
            HTTPStatus.UNAUTHORIZED,
        ),
        (
            {
                USERNAME_FIELD: f"bad{EMAIL_TEST_USER}",
                PASSWORD_FIELD: PASSWORD_TEST_USER,
            },
            HTTPStatus.UNAUTHORIZED,
        ),
        (
            {"bad_key": EMAIL_TEST_USER, PASSWORD_FIELD: PASSWORD_TEST_USER},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {USERNAME_FIELD: EMAIL_TEST_USER},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {PASSWORD_FIELD: PASSWORD_TEST_USER},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
    ],
)
async def test_login_errors(
    update_user_data: dict[str, str],
    status_code: int,
    client: AsyncClient,
    user_token_headers: dict[str, str],
) -> None:
    response = await client.post("api/v1/login", data=update_user_data)
    assert response.status_code == status_code


async def test_auth_user(
    client: AsyncClient, user_token_headers: dict[str, str]
) -> None:
    response = await client.get(
        "api/v1/users/me",
        headers=user_token_headers,
    )
    assert response.status_code == HTTPStatus.OK
    assert "email" in response.json()
    assert response.json()["email"] == EMAIL_TEST_USER


@pytest.mark.parametrize(
    "header, header_code, status_code",
    [
        ("Authorization", "no bearer", HTTPStatus.UNAUTHORIZED),
        ("Authorization", "invalid", HTTPStatus.UNAUTHORIZED),
        ("Bad_header", "valid", HTTPStatus.UNAUTHORIZED),
    ],
)
async def test_auth_user_errors(  # noqa: WPS211
    header: str,
    header_code: str,
    status_code: int,
    client: AsyncClient,
    valid_access_token: str,
    invalid_access_token: str,
) -> None:
    if header_code == "no bearer":
        header_value = valid_access_token
    elif header_code == "invalid":
        header_value = f"Bearer {invalid_access_token}"
    elif header_code == "valid":
        header_value = f"Bearer {valid_access_token}"
    else:
        raise ValueError(
            f"Unexpected header value {header_code} in test_auth_user_errors"
        )

    headers = {header: header_value}
    response = await client.get(
        "api/v1/users/me",
        headers=headers,
    )
    assert response.status_code == status_code


async def test_access_token_expire(
    client: AsyncClient, user_token_headers: dict[str, str]
) -> None:
    expired_after = timedelta(
        minutes=settings.access_token_expire_minutes, seconds=1
    )
    with freeze_time(expired_after):
        response = await client.get(
            "api/v1/users/me", headers=user_token_headers
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
