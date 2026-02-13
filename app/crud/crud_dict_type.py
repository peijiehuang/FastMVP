from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.sys_dict_type import SysDictType
from app.models.sys_dict_data import SysDictData
from app.schemas.sys_dict import DictTypeCreate, DictTypeUpdate


class CRUDDictType(CRUDBase[SysDictType, DictTypeCreate, DictTypeUpdate]):

    async def get_dict_type_list(
        self,
        db: AsyncSession,
        *,
        page_num: int = 1,
        page_size: int = 10,
        dict_name: str | None = None,
        dict_type: str | None = None,
        status: str | None = None,
        begin_time: str | None = None,
        end_time: str | None = None,
    ) -> tuple[Sequence[SysDictType], int]:
        query = select(SysDictType)
        if dict_name:
            query = query.where(SysDictType.dict_name.like(f"%{dict_name}%"))
        if dict_type:
            query = query.where(SysDictType.dict_type.like(f"%{dict_type}%"))
        if status:
            query = query.where(SysDictType.status == status)
        if begin_time:
            query = query.where(SysDictType.create_time >= begin_time)
        if end_time:
            query = query.where(SysDictType.create_time <= end_time)
        query = query.order_by(SysDictType.dict_id)
        return await self.get_list(db, query=query, page_num=page_num, page_size=page_size)

    async def get_all_dict_types(self, db: AsyncSession) -> Sequence[SysDictType]:
        result = await db.execute(select(SysDictType).order_by(SysDictType.dict_id))
        return result.scalars().all()

    async def get_by_type(self, db: AsyncSession, dict_type: str) -> SysDictType | None:
        result = await db.execute(
            select(SysDictType).where(SysDictType.dict_type == dict_type)
        )
        return result.scalar_one_or_none()

    async def create_dict_type(self, db: AsyncSession, obj_in: DictTypeCreate, create_by: str) -> SysDictType:
        dt = SysDictType(**obj_in.model_dump(), create_by=create_by)
        db.add(dt)
        await db.flush()
        await db.refresh(dt)
        return dt

    async def update_dict_type(self, db: AsyncSession, obj_in: DictTypeUpdate, update_by: str) -> SysDictType | None:
        dt = await self.get(db, obj_in.dict_id)
        if not dt:
            return None
        old_type = dt.dict_type
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"dict_id"})
        update_data["update_by"] = update_by
        update_data["update_time"] = datetime.now()
        new_type = update_data.get("dict_type", old_type)
        for k, v in update_data.items():
            setattr(dt, k, v)
        # Update dict_data if type changed
        if new_type != old_type:
            from sqlalchemy import update
            await db.execute(
                update(SysDictData).where(SysDictData.dict_type == old_type).values(dict_type=new_type)
            )
        await db.flush()
        return dt


crud_dict_type = CRUDDictType(SysDictType)
