from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.sys_dept import SysDept
from app.schemas.sys_dept import DeptCreate, DeptUpdate


class CRUDDept(CRUDBase[SysDept, DeptCreate, DeptUpdate]):

    async def get_all_depts(
        self,
        db: AsyncSession,
        *,
        dept_name: str | None = None,
        status: str | None = None,
    ) -> Sequence[SysDept]:
        """Get all departments (flat list, frontend builds tree)."""
        query = select(SysDept).where(SysDept.del_flag == "0")
        if dept_name:
            query = query.where(SysDept.dept_name.like(f"%{dept_name}%"))
        if status:
            query = query.where(SysDept.status == status)
        query = query.order_by(SysDept.parent_id, SysDept.order_num)
        result = await db.execute(query)
        return result.scalars().all()

    async def create_dept(self, db: AsyncSession, dept_in: DeptCreate, create_by: str) -> SysDept:
        # Build ancestors
        ancestors = ""
        if dept_in.parent_id > 0:
            parent = await self.get(db, dept_in.parent_id)
            if parent:
                ancestors = f"{parent.ancestors},{dept_in.parent_id}"
            else:
                ancestors = f"0,{dept_in.parent_id}"
        else:
            ancestors = "0"

        dept = SysDept(
            **dept_in.model_dump(),
            ancestors=ancestors,
            create_by=create_by,
        )
        db.add(dept)
        await db.flush()
        await db.refresh(dept)
        return dept

    async def update_dept(self, db: AsyncSession, dept_in: DeptUpdate, update_by: str) -> SysDept | None:
        dept = await self.get(db, dept_in.dept_id)
        if not dept:
            return None

        old_ancestors = dept.ancestors
        new_ancestors = old_ancestors

        update_data = dept_in.model_dump(exclude_unset=True, exclude={"dept_id"})

        # If parent changed, update ancestors
        if "parent_id" in update_data and update_data["parent_id"] != dept.parent_id:
            parent = await self.get(db, update_data["parent_id"])
            if parent:
                new_ancestors = f"{parent.ancestors},{update_data['parent_id']}"
            else:
                new_ancestors = f"0,{update_data['parent_id']}"
            update_data["ancestors"] = new_ancestors

            # Update all children's ancestors
            children = await db.execute(
                select(SysDept).where(SysDept.ancestors.like(f"%,{dept.dept_id},%") | SysDept.ancestors.like(f"%,{dept.dept_id}"))
            )
            for child in children.scalars().all():
                child.ancestors = child.ancestors.replace(old_ancestors, new_ancestors, 1)

        update_data["update_by"] = update_by
        update_data["update_time"] = datetime.now()
        for k, v in update_data.items():
            setattr(dept, k, v)
        await db.flush()
        return dept

    async def soft_delete(self, db: AsyncSession, dept_id: int) -> bool:
        dept = await self.get(db, dept_id)
        if not dept:
            return False
        # Check children
        result = await db.execute(
            select(SysDept).where(SysDept.parent_id == dept_id, SysDept.del_flag == "0")
        )
        if result.scalars().first():
            return False  # Has children
        dept.del_flag = "2"
        await db.flush()
        return True

    async def get_exclude_child(self, db: AsyncSession, dept_id: int) -> Sequence[SysDept]:
        """Get all depts excluding the given dept and its children."""
        query = select(SysDept).where(
            SysDept.del_flag == "0",
            SysDept.dept_id != dept_id,
            ~SysDept.ancestors.like(f"%,{dept_id},%"),
            ~SysDept.ancestors.like(f"%,{dept_id}"),
        ).order_by(SysDept.parent_id, SysDept.order_num)
        result = await db.execute(query)
        return result.scalars().all()


crud_dept = CRUDDept(SysDept)
