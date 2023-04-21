from uuid import UUID

from sqlalchemy.orm import DeclarativeBase, Mapped


class Base(DeclarativeBase):
    # make mypy happy, must be overridden in models
    id: Mapped[int] | Mapped[UUID]
