from datetime import datetime
from typing import Sequence

from sqlalchemy import Select, delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.associations import sys_role_dept, sys_role_menu, sys_user_role
from app.models.sys_role import SysRole
from app.models.sys_user import SysUser
from app.schemas.sys_role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[SysRole, RoleCreate, RoleUpdate]):

    async def get_role_list(
        self,
        db: AsyncSession,
        *,
        page_num: int = 1,
        page_size: int = 10,
        role_name: str | None = None,
        role_key: str | None = None,
        status: str | None = None,
        begin_time: str | None = None,
        end_time: str | None = None,
    ) -> tuple[Sequence[SysRole], int]:
        query = select(SysRole).where(SysRole.del_flag == "0")

        if role_name:
            query = query.where(SysRole.role_name.like(f"%{role_name}%"))
        if role_key:
            query = query.where(SysRole.role_key.like(f"%{role_key}%"))
        if status:
            query = query.where(SysRole.status == status)
        if begin_time:
            query = query.where(SysRole.create_time >= begin_time)
        if end_time:
            query = query.where(SysRole.create_time <= end_time)

        query = query.order_by(SysRole.role_sort)
        return await self.get_list(db, query=query, page_num=page_num, page_size=page_size)

    async def get_all_roles(self, db: AsyncSession) -> Sequence[SysRole]:
        stmt = select(SysRole).where(SysRole.del_flag == "0").order_by(SysRole.role_sort)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_role(
        self, db: AsyncSession, role_in: RoleCreate, create_by: str
    ) -> SysRole:
        role = SysRole(
            role_name=role_in.role_name,
            role_key=role_in.role_key,
            role_sort=role_in.role_sort,
            data_scope=role_in.data_scope,
            menu_check_strictly=role_in.menu_check_strictly,
            dept_check_strictly=role_in.dept_check_strictly,
            status=role_in.status,
            remark=role_in.remark,
            create_by=create_by,
        )
        db.add(role)
        await db.flush()

        if role_in.menu_ids:
            await db.execute(
                insert(sys_role_menu),
                [{"role_id": role.role_id, "menu_id": mid} for mid in role_in.menu_ids],
            )
        await db.refresh(role)
        return role

    async def update_role(
        self, db: AsyncSession, role_in: RoleUpdate, update_by: str
    ) -> SysRole | None:
        role = await self.get(db, role_in.role_id)
        if not role:
            return None

        update_data = role_in.model_dump(exclude_unset=True, exclude={"role_id", "menu_ids"})
        update_data["update_by"] = update_by
        update_data["update_time"] = datetime.now()
        for k, v in update_data.items():
            setattr(role, k, v)

        # Update menu relations
        await db.execute(delete(sys_role_menu).where(sys_role_menu.c.role_id == role.role_id))
        if role_in.menu_ids:
            await db.execute(
                insert(sys_role_menu),
                [{"role_id": role.role_id, "menu_id": mid} for mid in role_in.menu_ids],
            )

        await db.flush()
        await db.refresh(role)
        return role

    async def update_data_scope(
        self, db: AsyncSession, role_id: int, data_scope: str, dept_ids: list[int], update_by: str
    ):
        role = await self.get(db, role_id)
        if not role:
            return None
        role.data_scope = data_scope
        role.update_by = update_by
        role.update_time = datetime.now()

        await db.execute(delete(sys_role_dept).where(sys_role_dept.c.role_id == role_id))
        if dept_ids:
            await db.execute(
                insert(sys_role_dept),
                [{"role_id": role_id, "dept_id": did} for did in dept_ids],
            )
        await db.flush()
        return role

    async def soft_delete(self, db: AsyncSession, role_ids: list[int]) -> int:
        count = 0
        for rid in role_ids:
            role = await self.get(db, rid)
            if role and role.role_id != 1:  # Cannot delete admin role
                role.del_flag = "2"
                # Clean up relations
                await db.execute(delete(sys_role_menu).where(sys_role_menu.c.role_id == rid))
                await db.execute(delete(sys_role_dept).where(sys_role_dept.c.role_id == rid))
                count += 1
        await db.flush()
        return count

    async def update_status(self, db: AsyncSession, role_id: int, status: str, update_by: str):
        role = await self.get(db, role_id)
        if role:
            role.status = status
            role.update_by = update_by
            role.update_time = datetime.now()
            await db.flush()

    async def get_allocated_users(
        self, db: AsyncSession, role_id: int, *, page_num: int = 1, page_size: int = 10,
        user_name: str | None = None, phonenumber: str | None = None,
    ) -> tuple[Sequence[SysUser], int]:
        """Get users that have this role."""
        query = (
            select(SysUser)
            .join(sys_user_role, sys_user_role.c.user_id == SysUser.user_id)
            .where(sys_user_role.c.role_id == role_id, SysUser.del_flag == "0")
        )
        if user_name:
            query = query.where(SysUser.user_name.like(f"%{user_name}%"))
        if phonenumber:
            query = query.where(SysUser.phonenumber.like(f"%{phonenumber}%"))
        return await self.get_list(db, query=query, page_num=page_num, page_size=page_size)

    async def get_unallocated_users(
        self, db: AsyncSession, role_id: int, *, page_num: int = 1, page_size: int = 10,
        user_name: str | None = None, phonenumber: str | None = None,
    ) -> tuple[Sequence[SysUser], int]:
        """Get users that do not have this role."""
        allocated_ids = select(sys_user_role.c.user_id).where(
            sys_user_role.c.role_id == role_id
        )
        query = select(SysUser).where(
            SysUser.del_flag == "0",
            SysUser.user_id.not_in(allocated_ids),
        )
        if user_name:
            query = query.where(SysUser.user_name.like(f"%{user_name}%"))
        if phonenumber:
            query = query.where(SysUser.phonenumber.like(f"%{phonenumber}%"))
        return await self.get_list(db, query=query, page_num=page_num, page_size=page_size)

    async def cancel_auth_user(self, db: AsyncSession, user_id: int, role_id: int):
        await db.execute(
            delete(sys_user_role).where(
                sys_user_role.c.user_id == user_id,
                sys_user_role.c.role_id == role_id,
            )
        )

    async def cancel_auth_users(self, db: AsyncSession, role_id: int, user_ids: list[int]):
        await db.execute(
            delete(sys_user_role).where(
                sys_user_role.c.role_id == role_id,
                sys_user_role.c.user_id.in_(user_ids),
            )
        )

    async def select_auth_users(self, db: AsyncSession, role_id: int, user_ids: list[int]):
        for uid in user_ids:
            await db.execute(
                insert(sys_user_role).prefix_with("IGNORE"),
                [{"user_id": uid, "role_id": role_id}],
            )


crud_role = CRUDRole(SysRole)
