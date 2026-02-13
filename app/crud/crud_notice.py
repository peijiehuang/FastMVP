from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.sys_notice import SysNotice
from app.schemas.sys_notice import NoticeCreate, NoticeUpdate


class CRUDNotice(CRUDBase[SysNotice, NoticeCreate, NoticeUpdate]):

    async def get_notice_list(
        self,
        db: AsyncSession,
        *,
        page_num: int = 1,
        page_size: int = 10,
        notice_title: str | None = None,
        notice_type: str | None = None,
        create_by: str | None = None,
    ) -> tuple[Sequence[SysNotice], int]:
        query = select(SysNotice)
        if notice_title:
            query = query.where(SysNotice.notice_title.like(f"%{notice_title}%"))
        if notice_type:
            query = query.where(SysNotice.notice_type == notice_type)
        if create_by:
            query = query.where(SysNotice.create_by.like(f"%{create_by}%"))
        query = query.order_by(SysNotice.notice_id.desc())
        return await self.get_list(db, query=query, page_num=page_num, page_size=page_size)

    async def create_notice(self, db: AsyncSession, obj_in: NoticeCreate, create_by: str) -> SysNotice:
        notice = SysNotice(**obj_in.model_dump(), create_by=create_by)
        db.add(notice)
        await db.flush()
        await db.refresh(notice)
        return notice

    async def update_notice(self, db: AsyncSession, obj_in: NoticeUpdate, update_by: str) -> SysNotice | None:
        notice = await self.get(db, obj_in.notice_id)
        if not notice:
            return None
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"notice_id"})
        update_data["update_by"] = update_by
        update_data["update_time"] = datetime.now()
        for k, v in update_data.items():
            setattr(notice, k, v)
        await db.flush()
        return notice


crud_notice = CRUDNotice(SysNotice)
