from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.sys_post import SysPost
from app.schemas.sys_post import PostCreate, PostUpdate


class CRUDPost(CRUDBase[SysPost, PostCreate, PostUpdate]):

    async def get_post_list(
        self,
        db: AsyncSession,
        *,
        page_num: int = 1,
        page_size: int = 10,
        post_code: str | None = None,
        post_name: str | None = None,
        status: str | None = None,
    ) -> tuple[Sequence[SysPost], int]:
        query = select(SysPost)
        if post_code:
            query = query.where(SysPost.post_code.like(f"%{post_code}%"))
        if post_name:
            query = query.where(SysPost.post_name.like(f"%{post_name}%"))
        if status:
            query = query.where(SysPost.status == status)
        query = query.order_by(SysPost.post_sort)
        return await self.get_list(db, query=query, page_num=page_num, page_size=page_size)

    async def get_all_posts(self, db: AsyncSession) -> Sequence[SysPost]:
        stmt = select(SysPost).order_by(SysPost.post_sort)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_post(self, db: AsyncSession, post_in: PostCreate, create_by: str) -> SysPost:
        post = SysPost(**post_in.model_dump(), create_by=create_by)
        db.add(post)
        await db.flush()
        await db.refresh(post)
        return post

    async def update_post(self, db: AsyncSession, post_in: PostUpdate, update_by: str) -> SysPost | None:
        post = await self.get(db, post_in.post_id)
        if not post:
            return None
        update_data = post_in.model_dump(exclude_unset=True, exclude={"post_id"})
        update_data["update_by"] = update_by
        update_data["update_time"] = datetime.now()
        for k, v in update_data.items():
            setattr(post, k, v)
        await db.flush()
        return post


crud_post = CRUDPost(SysPost)
