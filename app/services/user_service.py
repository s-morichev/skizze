from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.models import Permission, Role, User
from app.schemas import UserCreate, UserUpdate
from app.services.crud_base import CRUDBase

PASSWORD_FIELD = "password"  # noqa: S105


class UserService(CRUDBase[User, UserCreate, UserUpdate]):
    async def create(
        self, session: AsyncSession, *, obj_in: UserCreate
    ) -> User:
        obj_in_dict = obj_in.dict(exclude={PASSWORD_FIELD})
        db_obj = self.model(
            **obj_in_dict, password_hash=get_password_hash(obj_in.password)
        )
        db_result = await session.execute(
            (select(Role).filter_by(default=True))
        )
        default_role = db_result.scalar_one()
        db_obj.role = default_role
        session.add(db_obj)
        await session.commit()
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: User,
        obj_in: UserUpdate | dict[str, Any],
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # обновляем password hash
        new_password = update_data.get(PASSWORD_FIELD)
        if new_password:
            db_obj.password_hash = get_password_hash(new_password)
            session.add(db_obj)
            await session.commit()
            update_data.pop(PASSWORD_FIELD)

        # обновляем остальные поля
        return await super().update(session, db_obj=db_obj, obj_in=update_data)

    async def get_by_email(
        self, session: AsyncSession, *, email: str
    ) -> User | None:
        stmt = select(User).filter(User.email == email)
        return (await session.scalars(stmt)).one_or_none()

    async def authenticate(
        self, session: AsyncSession, *, email: str, password: str
    ) -> User | None:
        user = await self.get_by_email(session, email=email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def user_has_permission(self, user: User, permission: Permission) -> bool:
        return user.role.permissions & permission == permission


crud_user = UserService(User)
