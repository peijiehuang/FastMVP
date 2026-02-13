from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.sys_oper_log import SysOperLog


class CRUDOperLog(CRUDBase[SysOperLog, None, None]):

    async def get_oper_log_list(
        self,
        db: AsyncSession,
        *,
        page_num: int = 1,
        page_size: int = 10,
        title: str | None = None,
        business_type: int | None = None,
        oper_name: str | None = None,
        status: int | None = None,
        begin_time: str | None = None,
        end_time: str | None = None,
    ) -> tuple[Sequence[SysOperLog], int]:
        query = select(SysOperLog)
        if title:
            query = query.where(SysOperLog.title.like(f"%{title}%"))
        if business_type is not None:
            query = query.where(SysOperLog.business_type == business_type)
        if oper_name:
            query = query.where(SysOperLog.oper_name.like(f"%{oper_name}%"))
        if status is not None:
            query = query.where(SysOperLog.status == status)
        if begin_time:
            query = query.where(SysOperLog.oper_time >= begin_time)
        if end_time:
            query = query.where(SysOperLog.oper_time <= end_time)
        query = query.order_by(SysOperLog.oper_id.desc())
        return await self.get_list(db, query=query, page_num=page_num, page_size=page_size)

    async def add_log(self, db: AsyncSession, log: SysOperLog):
        db.add(log)
        await db.flush()

    async def clean(self, db: AsyncSession):
        await db.execute(delete(SysOperLog))


crud_oper_log = CRUDOperLog(SysOperLog)
