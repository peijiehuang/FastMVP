from typing import Any, Generic, Sequence, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import Select, func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic CRUD base class with pagination support."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        result = await db.execute(
            select(self.model).where(self._pk_column() == id)
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        db: AsyncSession,
        *,
        query: Select | None = None,
        page_num: int = 1,
        page_size: int = 10,
    ) -> tuple[Sequence[ModelType], int]:
        """Get paginated list. Returns (items, total_count)."""
        if query is None:
            query = select(self.model)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        offset = (page_num - 1) * page_size
        paginated = query.offset(offset).limit(page_size)
        result = await db.execute(paginated)
        items = result.scalars().all()

        return items, total

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType, **extra) -> ModelType:
        data = obj_in.model_dump(exclude_unset=True)
        data.update(extra)
        db_obj = self.model(**data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType | dict
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete_by_ids(self, db: AsyncSession, ids: list[Any]) -> int:
        """Delete multiple records by primary key IDs."""
        stmt = delete(self.model).where(self._pk_column().in_(ids))
        result = await db.execute(stmt)
        return result.rowcount

    def _pk_column(self):
        """Get the primary key column of the model."""
        pk_columns = self.model.__table__.primary_key.columns
        return list(pk_columns)[0]
