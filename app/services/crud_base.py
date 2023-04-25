from collections.abc import Sequence
from typing import Any, Generic, TypeVar
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base_class import Base
from app.schemas.base_class import BaseSchema

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def create(
        self, session: AsyncSession, *, obj_in: CreateSchemaType
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def read(
        self, session: AsyncSession, id_: int | UUID
    ) -> ModelType | None:
        stmt = select(self.model).filter(self.model.id == id_)
        return (await session.scalars(stmt)).one_or_none()

    async def read_multi(
        self, session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        return (await session.scalars(stmt)).all()

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data.get(field))
        session.add(db_obj)
        await session.commit()
        return db_obj

    async def delete(
        self, session: AsyncSession, *, id_: int | UUID
    ) -> ModelType | None:
        stmt = delete(self.model).where(self.model.id == id_)
        await session.commit()
        return (await session.scalars(stmt)).one_or_none()
