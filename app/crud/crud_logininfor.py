from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.sys_logininfor import SysLogininfor


class CRUDLogininfor(CRUDBase[SysLogininfor, None, None]):

    async def get_logininfor_list(
        self,
        db: AsyncSession,
        *,
        page_num: int = 1,
        page_size: int = 10,
        user_name: str | None = None,
        ipaddr: str | None = None,
        status: str | None = None,
        begin_time: str | None = None,
        end_time: str | None = None,
    ) -> tuple[Sequence[SysLogininfor], int]:
        query = select(SysLogininfor)
        if user_name:
            query = query.where(SysLogininfor.user_name.like(f"%{user_name}%"))
        if ipaddr:
            query = query.where(SysLogininfor.ipaddr.like(f"%{ipaddr}%"))
        if status:
            query = query.where(SysLogininfor.status == status)
        if begin_time:
            query = query.where(SysLogininfor.login_time >= begin_time)
        if end_time:
            query = query.where(SysLogininfor.login_time <= end_time)
        query = query.order_by(SysLogininfor.info_id.desc())
        return await self.get_list(db, query=query, page_num=page_num, page_size=page_size)

    async def add_log(self, db: AsyncSession, log: SysLogininfor):
        db.add(log)
        await db.flush()

    async def clean(self, db: AsyncSession):
        await db.execute(delete(SysLogininfor))


crud_logininfor = CRUDLogininfor(SysLogininfor)
