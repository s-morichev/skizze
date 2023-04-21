from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.api import deps
from app.models import models
from app.services.user_service import crud_user

router = APIRouter()


@router.get("/me", response_model=schemas.User)
async def read_current_user(
    current_user: models.User = Depends(deps.get_current_user),
) -> models.User:
    return current_user


@router.patch("/me", response_model=schemas.User)
async def update_current_user(
    user_in: schemas.UserUpdate,
    session: AsyncSession = Depends(deps.get_session),
    current_user: models.User = Depends(deps.get_current_user),
) -> models.User:
    return await crud_user.update(session, db_obj=current_user, obj_in=user_in)


@router.post("", response_model=schemas.User)
async def create_user(
    user_in: schemas.UserCreate,
    session: AsyncSession = Depends(deps.get_session),
) -> models.User:
    return await crud_user.create(session, obj_in=user_in)


@router.get("/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: UUID, session: AsyncSession = Depends(deps.get_session)
) -> models.User:
    user = await crud_user.read(session, user_id)
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )

    return user
