from functools import partial
from http import HTTPStatus
from typing import Any, AsyncGenerator

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_jwt_token
from app.db.session import async_session
from app.models import models
from app.services.user_service import crud_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    jwt_token: str = Depends(oauth2_scheme),
) -> models.User:
    token = decode_jwt_token(jwt_token)
    if token is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = await crud_user.read(session, id_=token.sub)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )
    return user


def check_permission(
    permission: models.Permission, user: models.User = Depends(get_current_user)
) -> None:
    if not crud_user.user_has_permission(user, permission):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="No permission"
        )


def permission_required(permission: models.Permission) -> Any:
    permission_deps = partial(check_permission, permission=permission)
    return Depends(permission_deps)
