from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.sys_job_log import SysJobLog


class CRUDJobLog(CRUDBase[SysJobLog, None, None]):

    async def get_job_log_list(
        self,
        db: AsyncSession,
        *,
        page_num: int = 1,
        page_size: int = 10,
        job_name: str | None = None,
        job_group: str | None = None,
        status: str | None = None,
        begin_time: str | None = None,
        end_time: str | None = None,
    ) -> tuple[Sequence[SysJobLog], int]:
        query = select(SysJobLog)
        if job_name:
            query = query.where(SysJobLog.job_name.like(f"%{job_name}%"))
        if job_group:
            query = query.where(SysJobLog.job_group == job_group)
        if status is not None:
            query = query.where(SysJobLog.status == status)
        if begin_time:
            query = query.where(SysJobLog.create_time >= begin_time)
        if end_time:
            query = query.where(SysJobLog.create_time <= end_time)
        query = query.order_by(SysJobLog.job_log_id.desc())
        return await self.get_list(db, query=query, page_num=page_num, page_size=page_size)

    async def clean(self, db: AsyncSession):
        await db.execute(delete(SysJobLog))


crud_job_log = CRUDJobLog(SysJobLog)
