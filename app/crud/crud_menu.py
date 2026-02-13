from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.sys_menu import SysMenu
from app.schemas.sys_menu import MenuCreate, MenuUpdate


class CRUDMenu(CRUDBase[SysMenu, MenuCreate, MenuUpdate]):

    async def get_menu_list(
        self,
        db: AsyncSession,
        *,
        menu_name: str | None = None,
        status: str | None = None,
    ) -> Sequence[SysMenu]:
        """Get all menus (flat list, no pagination - frontend builds tree)."""
        query = select(SysMenu)
        if menu_name:
            query = query.where(SysMenu.menu_name.like(f"%{menu_name}%"))
        if status:
            query = query.where(SysMenu.status == status)
        query = query.order_by(SysMenu.parent_id, SysMenu.order_num)
        result = await db.execute(query)
        return result.scalars().all()

    async def create_menu(self, db: AsyncSession, menu_in: MenuCreate, create_by: str) -> SysMenu:
        menu = SysMenu(**menu_in.model_dump(), create_by=create_by)
        db.add(menu)
        await db.flush()
        await db.refresh(menu)
        return menu

    async def update_menu(self, db: AsyncSession, menu_in: MenuUpdate, update_by: str) -> SysMenu | None:
        menu = await self.get(db, menu_in.menu_id)
        if not menu:
            return None
        update_data = menu_in.model_dump(exclude_unset=True, exclude={"menu_id"})
        update_data["update_by"] = update_by
        update_data["update_time"] = datetime.now()
        for k, v in update_data.items():
            setattr(menu, k, v)
        await db.flush()
        return menu

    async def delete_menu(self, db: AsyncSession, menu_id: int) -> bool:
        # Check if has children
        result = await db.execute(
            select(SysMenu).where(SysMenu.parent_id == menu_id)
        )
        if result.scalars().first():
            return False  # Has children, cannot delete
        menu = await self.get(db, menu_id)
        if menu:
            await db.delete(menu)
            await db.flush()
        return True

    async def has_child(self, db: AsyncSession, menu_id: int) -> bool:
        result = await db.execute(
            select(SysMenu).where(SysMenu.parent_id == menu_id)
        )
        return result.scalars().first() is not None


crud_menu = CRUDMenu(SysMenu)
