from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.sys_dict_data import SysDictData
from app.schemas.sys_dict import DictDataCreate, DictDataUpdate


class CRUDDictData(CRUDBase[SysDictData, DictDataCreate, DictDataUpdate]):

    async def get_dict_data_list(
        self,
        db: AsyncSession,
        *,
        page_num: int = 1,
        page_size: int = 10,
        dict_type: str | None = None,
        dict_label: str | None = None,
        status: str | None = None,
    ) -> tuple[Sequence[SysDictData], int]:
        query = select(SysDictData)
        if dict_type:
            query = query.where(SysDictData.dict_type == dict_type)
        if dict_label:
            query = query.where(SysDictData.dict_label.like(f"%{dict_label}%"))
        if status:
            query = query.where(SysDictData.status == status)
        query = query.order_by(SysDictData.dict_sort)
        return await self.get_list(db, query=query, page_num=page_num, page_size=page_size)

    async def get_by_dict_type(self, db: AsyncSession, dict_type: str) -> Sequence[SysDictData]:
        result = await db.execute(
            select(SysDictData)
            .where(SysDictData.dict_type == dict_type, SysDictData.status == "0")
            .order_by(SysDictData.dict_sort)
        )
        return result.scalars().all()

    async def create_dict_data(self, db: AsyncSession, obj_in: DictDataCreate, create_by: str) -> SysDictData:
        dd = SysDictData(**obj_in.model_dump(), create_by=create_by)
        db.add(dd)
        await db.flush()
        await db.refresh(dd)
        return dd

    async def update_dict_data(self, db: AsyncSession, obj_in: DictDataUpdate, update_by: str) -> SysDictData | None:
        dd = await self.get(db, obj_in.dict_code)
        if not dd:
            return None
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"dict_code"})
        update_data["update_by"] = update_by
        update_data["update_time"] = datetime.now()
        for k, v in update_data.items():
            setattr(dd, k, v)
        await db.flush()
        return dd


crud_dict_data = CRUDDictData(SysDictData)
