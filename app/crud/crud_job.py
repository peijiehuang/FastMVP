from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.sys_job import SysJob
from app.schemas.sys_job import JobCreate, JobUpdate


class CRUDJob(CRUDBase[SysJob, JobCreate, JobUpdate]):

    async def get_job_list(
        self,
        db: AsyncSession,
        *,
        page_num: int = 1,
        page_size: int = 10,
        job_name: str | None = None,
        job_group: str | None = None,
        status: str | None = None,
    ) -> tuple[Sequence[SysJob], int]:
        query = select(SysJob)
        if job_name:
            query = query.where(SysJob.job_name.like(f"%{job_name}%"))
        if job_group:
            query = query.where(SysJob.job_group == job_group)
        if status is not None:
            query = query.where(SysJob.status == status)
        query = query.order_by(SysJob.job_id)
        return await self.get_list(db, query=query, page_num=page_num, page_size=page_size)

    async def get_all_enabled(self, db: AsyncSession) -> Sequence[SysJob]:
        result = await db.execute(select(SysJob).where(SysJob.status == "0"))
        return result.scalars().all()

    async def create_job(self, db: AsyncSession, obj_in: JobCreate, create_by: str) -> SysJob:
        job = SysJob(**obj_in.model_dump(), create_by=create_by)
        db.add(job)
        await db.flush()
        await db.refresh(job)
        return job

    async def update_job(self, db: AsyncSession, obj_in: JobUpdate, update_by: str) -> SysJob | None:
        job = await self.get(db, obj_in.job_id)
        if not job:
            return None
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"job_id"})
        update_data["update_by"] = update_by
        update_data["update_time"] = datetime.now()
        for k, v in update_data.items():
            setattr(job, k, v)
        await db.flush()
        return job


crud_job = CRUDJob(SysJob)
