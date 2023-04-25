from enum import IntEnum
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_class import Base
from app.models.mixins import IntegerIdMixin, TimeStampedMixin, UUIDIdMixin

STRING_COLUMN_DEFAULT_LEN = 255
STRING_COLUMN_HASH_LEN = 128


class Permission(IntEnum):
    follow = 1
    comment = 2
    write = 2**2
    moderate = 2**3
    admin = 2**4


class Role(IntegerIdMixin, Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(
        String(STRING_COLUMN_DEFAULT_LEN), unique=True
    )
    default: Mapped[bool] = mapped_column(Boolean, default=False)
    permissions: Mapped[int]
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="role", lazy="raise"
    )

    def __repr__(self) -> str:
        return f"<Role {self.name}>"


class User(UUIDIdMixin, TimeStampedMixin, Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(
        String(STRING_COLUMN_DEFAULT_LEN), unique=True, index=True
    )
    username: Mapped[str | None] = mapped_column(
        String(STRING_COLUMN_DEFAULT_LEN), unique=True, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(STRING_COLUMN_HASH_LEN))
    about_me: Mapped[str] = mapped_column(
        String(STRING_COLUMN_DEFAULT_LEN), default=""
    )
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    role: Mapped["Role"] = relationship(
        "Role", back_populates="users", lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"
