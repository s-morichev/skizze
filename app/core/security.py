from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
from pydantic import ValidationError

from app import schemas
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta | None = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decode_jwt_token(token: str) -> schemas.TokenPayload | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError:
        return None
    try:
        token_data = schemas.TokenPayload(**payload)
    except ValidationError:
        return None

    return token_data


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
