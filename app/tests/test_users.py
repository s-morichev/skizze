from http import HTTPStatus

import pytest
from httpx import AsyncClient

from app.tests.constants import (
    EMAIL_FIELD,
    EMAIL_TEST_USER,
    PASSWORD_FIELD,
    PASSWORD_TEST_USER,
    USERNAME_FIELD,
)

pytestmark = pytest.mark.asyncio


async def test_create_user(client: AsyncClient) -> None:
    response = await client.post(
        "api/v1/users",
        json={
            EMAIL_FIELD: "test_create_user@example.com",
            USERNAME_FIELD: "test_create_user",
            PASSWORD_FIELD: "test_password",
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()[EMAIL_FIELD] == "test_create_user@example.com"
    assert response.json()[USERNAME_FIELD] == "test_create_user"


async def test_read_current_user(
    client: AsyncClient, user_token_headers: dict[str, str]
) -> None:
    response = await client.get("api/v1/users/me", headers=user_token_headers)
    assert response.status_code == HTTPStatus.OK
    assert response.json()[EMAIL_FIELD] == EMAIL_TEST_USER


async def test_update_current_user(
    client: AsyncClient, user_token_headers: dict[str, str]
) -> None:
    update = {"about_me": "about_me"}
    response = await client.patch(
        "api/v1/users/me", json=update, headers=user_token_headers
    )
    assert response.status_code == HTTPStatus.OK
    for key, correct_value in update.items():
        assert response.json()[key] == correct_value


async def test_update_current_user_password(
    client: AsyncClient, user_token_headers: dict[str, str]
) -> None:
    new_password = f"new{PASSWORD_TEST_USER}"
    response = await client.patch(
        "api/v1/users/me",
        json={PASSWORD_FIELD: new_password},
        headers=user_token_headers,
    )
    assert response.status_code == HTTPStatus.OK

    response = await client.post(
        "api/v1/login",
        data={USERNAME_FIELD: EMAIL_TEST_USER, PASSWORD_FIELD: new_password},
    )
    assert response.status_code == HTTPStatus.OK


async def test_read_user(client: AsyncClient) -> None:
    response = await client.post(
        "api/v1/users",
        json={
            "email": "test_read_user@example.com",
            USERNAME_FIELD: "test_read_user",
            PASSWORD_FIELD: "test_password",
        },
    )
    assert response.status_code == HTTPStatus.OK
    user_id = response.json()["id"]

    response = await client.get(f"api/v1/users/{user_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["email"] == "test_read_user@example.com"
