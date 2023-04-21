from datetime import timedelta
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.services.user_service import crud_user

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
async def login_access_token(
    session: AsyncSession = Depends(deps.get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, str]:
    user = await crud_user.authenticate(
        session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
