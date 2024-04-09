from typing import Type, Iterable

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import ColumnElement, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql._typing import _HasClauseElement
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.elements import SQLCoreOperations
from starlette import status

from src.database.db import Base
from src.schemas.filters import BaseFilterData


class SQLAlchemyRepository:
    model: Type[Base] = None

    async def create_object(
            self,
            session: AsyncSession,
            data: BaseModel,
            model_schema: Type[BaseModel],
            **additional_fields
    ):
        new_obj = self.model(**data.model_dump(), **additional_fields)
        session.add(new_obj)
        await session.commit()
        await session.refresh(new_obj)
        return model_schema.model_validate(new_obj, from_attributes=True)

    async def get_object(
            self,
            session: AsyncSession,
            expression: ColumnElement[bool] | _HasClauseElement[bool] | SQLCoreOperations[bool],
            model_schema: Type[BaseModel],
            options: Iterable[ExecutableOption] | ExecutableOption = None
    ):
        query = select(self.model).where(expression)

        if options:
            if isinstance(options, Iterable):
                for option in options:
                    query = query.options(option)
            else:
                query = query.options(options)

        result = await session.execute(query)
        _obj = result.scalar_one_or_none()

        if _obj is None:
            return _obj

        return model_schema.model_validate(_obj, from_attributes=True)

    async def get_objects(
            self,
            session: AsyncSession,
            model_schema: Type[BaseModel],
            limit: int = 1000,
            offset: int = 0,
            options:  Iterable[ExecutableOption]| ExecutableOption = None,
            expression: ColumnElement[bool] | _HasClauseElement[bool] | SQLCoreOperations[bool] = None,
            filter_data: BaseFilterData | None = None
    ):
        query = select(self.model).offset(offset).limit(limit)
        if expression:
            query = query.where(expression)

        if filter_data:
            query = query.filter_by(**filter_data.get_filter_data())

        if options:
            if isinstance(options, Iterable):
                for option in options:
                    query = query.options(option)
            else:
                query = query.options(options)

        result = await session.execute(query)
        return [model_schema.model_validate(obj, from_attributes=True) for obj in result.scalars().all()]

    async def update_object(
            self,
            session: AsyncSession,
            data: BaseModel,
            expression: ColumnElement[bool] | _HasClauseElement[bool] | SQLCoreOperations[bool],
    ) -> None:
        stmp = update(self.model).where(expression).values(**data.model_dump())
        await session.execute(stmp)
        await session.commit()

    async def delete_object(
            self,
            session: AsyncSession,
            expression: ColumnElement[bool] | _HasClauseElement[bool] | SQLCoreOperations[bool],

    ) -> None:
        stmp = delete(self.model).where(expression)
        await session.execute(stmp)
        await session.commit()

    async def get_one_object_by(
            self,
            session: AsyncSession,
            expression: ColumnElement[bool] | _HasClauseElement[bool] | SQLCoreOperations[bool],
            model_schema: Type[BaseModel],
            allow_none: bool = True
    ):
        query = select(self.model).where(expression)
        result = await session.execute(query)

        db_obj = result.scalar_one_or_none()

        if db_obj is None:
            if not allow_none:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Не найдено.')
            return None

        return model_schema.model_validate(db_obj, from_attributes=True)

    async def update_values(
            self,
            session: AsyncSession,
            expression: ColumnElement[bool] | _HasClauseElement[bool] | SQLCoreOperations[bool],
            **values
    ) -> None:
        stmp = update(self.model).where(expression).values(**values)
        await session.execute(stmp)
        await session.commit()