from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import UserCreate, UserUpdate
from app.services.user_service import crud_user


async def access_token(client: AsyncClient, email: str, password: str) -> str:
    auth_data = {"username": email, "password": password}
    response = await client.post("api/v1/login", data=auth_data)
    return str(response.json()["access_token"])


async def authentication_headers(
    client: AsyncClient, email: str, password: str
) -> dict[str, str]:
    token = await access_token(client, email, password)
    return {"Authorization": f"Bearer {token}"}


async def authenticate_user(
    client: AsyncClient, session: AsyncSession, email: str, password: str
) -> dict[str, str]:
    """
    Получить заголовок для авторизации пользователя.

    При необходимости создает пользователя или меняет пароль.
    """
    user = await crud_user.get_by_email(session, email=email)
    if user:
        user_update = UserUpdate(password=password)
        await crud_user.update(session, db_obj=user, obj_in=user_update)
    else:
        user_in = UserCreate(email=email, password=password, username=email)
        await crud_user.create(session, obj_in=user_in)

    return await authentication_headers(client, email, password)
