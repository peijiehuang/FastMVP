from datetime import datetime
from typing import Sequence

from sqlalchemy import Select, delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.associations import sys_user_post, sys_user_role
from app.models.sys_dept import SysDept
from app.models.sys_user import SysUser
from app.schemas.sys_user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[SysUser, UserCreate, UserUpdate]):

    async def get_by_username(self, db: AsyncSession, username: str) -> SysUser | None:
        stmt = select(SysUser).where(
            SysUser.user_name == username, SysUser.del_flag == "0"
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_list(
        self,
        db: AsyncSession,
        *,
        page_num: int = 1,
        page_size: int = 10,
        user_name: str | None = None,
        phonenumber: str | None = None,
        status: str | None = None,
        dept_id: int | None = None,
        begin_time: str | None = None,
        end_time: str | None = None,
    ) -> tuple[Sequence[SysUser], int]:
        query = select(SysUser).where(SysUser.del_flag == "0")

        if user_name:
            query = query.where(SysUser.user_name.like(f"%{user_name}%"))
        if phonenumber:
            query = query.where(SysUser.phonenumber.like(f"%{phonenumber}%"))
        if status:
            query = query.where(SysUser.status == status)
        if dept_id:
            # Include child departments
            query = query.where(
                SysUser.dept_id.in_(
                    select(SysDept.dept_id).where(
                        (SysDept.dept_id == dept_id)
                        | SysDept.ancestors.like(f"%,{dept_id},%")
                        | SysDept.ancestors.like(f"%,{dept_id}")
                    )
                )
            )
        if begin_time:
            query = query.where(SysUser.create_time >= begin_time)
        if end_time:
            query = query.where(SysUser.create_time <= end_time)

        query = query.order_by(SysUser.user_id)
        return await self.get_list(db, query=query, page_num=page_num, page_size=page_size)

    async def create_user(
        self, db: AsyncSession, user_in: UserCreate, password_hash: str, create_by: str
    ) -> SysUser:
        user = SysUser(
            dept_id=user_in.dept_id,
            user_name=user_in.user_name,
            nick_name=user_in.nick_name,
            password=password_hash,
            email=user_in.email,
            phonenumber=user_in.phonenumber,
            sex=user_in.sex,
            status=user_in.status,
            remark=user_in.remark,
            create_by=create_by,
        )
        db.add(user)
        await db.flush()

        # Insert user-role relations
        if user_in.role_ids:
            await db.execute(
                insert(sys_user_role),
                [{"user_id": user.user_id, "role_id": rid} for rid in user_in.role_ids],
            )
        # Insert user-post relations
        if user_in.post_ids:
            await db.execute(
                insert(sys_user_post),
                [{"user_id": user.user_id, "post_id": pid} for pid in user_in.post_ids],
            )

        await db.refresh(user)
        return user

    async def update_user(
        self, db: AsyncSession, user_in: UserUpdate, update_by: str
    ) -> SysUser:
        user = await self.get(db, user_in.user_id)
        if not user:
            return None

        update_data = user_in.model_dump(exclude_unset=True, exclude={"user_id", "post_ids", "role_ids"})
        update_data["update_by"] = update_by
        update_data["update_time"] = datetime.now()
        for k, v in update_data.items():
            setattr(user, k, v)

        # Update role relations
        await db.execute(delete(sys_user_role).where(sys_user_role.c.user_id == user.user_id))
        if user_in.role_ids:
            await db.execute(
                insert(sys_user_role),
                [{"user_id": user.user_id, "role_id": rid} for rid in user_in.role_ids],
            )

        # Update post relations
        await db.execute(delete(sys_user_post).where(sys_user_post.c.user_id == user.user_id))
        if user_in.post_ids:
            await db.execute(
                insert(sys_user_post),
                [{"user_id": user.user_id, "post_id": pid} for pid in user_in.post_ids],
            )

        await db.flush()
        await db.refresh(user)
        return user

    async def soft_delete(self, db: AsyncSession, user_ids: list[int]) -> int:
        """Soft delete users by setting del_flag to '2'."""
        count = 0
        for uid in user_ids:
            user = await self.get(db, uid)
            if user and user.user_id != 1:  # Cannot delete admin
                user.del_flag = "2"
                count += 1
        await db.flush()
        return count

    async def reset_password(self, db: AsyncSession, user_id: int, password_hash: str, update_by: str):
        user = await self.get(db, user_id)
        if user:
            user.password = password_hash
            user.update_by = update_by
            user.update_time = datetime.now()
            await db.flush()

    async def update_status(self, db: AsyncSession, user_id: int, status: str, update_by: str):
        user = await self.get(db, user_id)
        if user:
            user.status = status
            user.update_by = update_by
            user.update_time = datetime.now()
            await db.flush()

    async def update_avatar(self, db: AsyncSession, user_id: int, avatar: str):
        user = await self.get(db, user_id)
        if user:
            user.avatar = avatar
            await db.flush()


crud_user = CRUDUser(SysUser)
