from datetime import datetime
from uuid import UUID

from app.schemas.base_class import BaseSchema


class UserCreate(BaseSchema):
    """Схема для создания."""

    email: str
    password: str
    username: str


class UserUpdate(BaseSchema):
    """Схема для обновления."""

    password: str | None = None
    about_me: str = ""


class UserBase(BaseSchema):
    """Общие свойства кроме базы данных."""

    email: str
    username: str | None = None
    confirmed: bool = False
    about_me: str | None = None
    created_at: datetime | None = None


class UserInDBBase(UserBase):
    """Общие свойства в базе данных."""

    id: UUID | None = None

    class Config(object):
        orm_mode = True


class User(UserInDBBase):
    """Схема для возврата из API."""


class UserInDB(UserInDBBase):
    """Схема для хранения в базе данных."""

    hashed_password: str
