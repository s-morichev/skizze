import contextlib

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.base_class import Base
from app.models.models import Permission, Role
from app.schemas import UserCreate
from app.services.user_service import crud_user


async def recreate_tables(session: AsyncSession) -> None:
    conn = await session.connection()
    await conn.run_sync(Base.metadata.drop_all)
    await conn.run_sync(Base.metadata.create_all)


async def insert_roles(session: AsyncSession) -> None:
    roles = {
        "User": [Permission.follow, Permission.comment, Permission.write],
        "Moderator": [
            Permission.follow,
            Permission.comment,
            Permission.write,
            Permission.moderate,
        ],
        "Administrator": [
            Permission.follow,
            Permission.comment,
            Permission.write,
            Permission.moderate,
            Permission.admin,
        ],
    }
    default_role = "User"

    for role_name in roles.keys():
        role = Role(name=role_name)
        role.permissions = sum(roles[role_name])
        role.default = role.name == default_role
        session.add(role)

    with contextlib.suppress(IntegrityError):
        await session.commit()


async def create_admin(session: AsyncSession) -> None:
    admin_role = (
        await session.execute(select(Role).where(Role.name == "Administrator"))
    ).scalar_one()

    admin_create = UserCreate(
        email=settings.admin_email,
        username=settings.admin_email,
        password=settings.admin_password,
    )
    admin_user = await crud_user.create(session, obj_in=admin_create)
    admin_user.role = admin_role
    session.add(admin_user)
    await session.commit()
