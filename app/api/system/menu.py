from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import BusinessType
from app.core.decorators import log_operation
from app.core.deps import get_current_user, has_permi
from app.core.response import AjaxResult
from app.crud.crud_menu import crud_menu
from app.db.session import get_db
from app.models.associations import sys_role_menu
from app.schemas.sys_menu import MenuCreate, MenuUpdate

router = APIRouter()


def _menu_to_dict(m) -> dict:
    return {
        "menuId": m.menu_id,
        "menuName": m.menu_name,
        "parentId": m.parent_id,
        "orderNum": m.order_num,
        "path": m.path,
        "component": m.component,
        "query": m.query,
        "routeName": m.route_name,
        "isFrame": m.is_frame,
        "isCache": m.is_cache,
        "menuType": m.menu_type,
        "visible": m.visible,
        "status": m.status,
        "perms": m.perms,
        "icon": m.icon,
        "createBy": m.create_by,
        "createTime": m.create_time.strftime("%Y-%m-%d %H:%M:%S") if m.create_time else None,
        "children": [],
    }


@router.get("/list")
async def list_menus(
    current_user: dict = Depends(has_permi("system:menu:list")),
    db: AsyncSession = Depends(get_db),
    menuName: str | None = Query(None),
    status: str | None = Query(None),
):
    menus = await crud_menu.get_menu_list(db, menu_name=menuName, status=status)
    return AjaxResult.success(data=[_menu_to_dict(m) for m in menus])


@router.get("/treeselect")
async def treeselect(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    menus = await crud_menu.get_menu_list(db)
    tree = _build_menu_tree(menus, 0)
    return AjaxResult.success(data=tree)


@router.get("/roleMenuTreeselect/{role_id}")
async def role_menu_treeselect(
    role_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    menus = await crud_menu.get_menu_list(db)
    tree = _build_menu_tree(menus, 0)

    # Get checked menu IDs for this role
    result = await db.execute(
        select(sys_role_menu.c.menu_id).where(sys_role_menu.c.role_id == role_id)
    )
    checked_keys = [row[0] for row in result.fetchall()]

    return AjaxResult.success(checkedKeys=checked_keys, menus=tree)


@router.get("/{menu_id}")
async def get_menu(
    menu_id: int,
    current_user: dict = Depends(has_permi("system:menu:query")),
    db: AsyncSession = Depends(get_db),
):
    menu = await crud_menu.get(db, menu_id)
    if not menu:
        return AjaxResult.error(msg="菜单不存在")
    return AjaxResult.success(data=_menu_to_dict(menu))


@router.post("")
@log_operation("菜单管理", BusinessType.INSERT)
async def add_menu(
    body: MenuCreate,
    request: Request,
    current_user: dict = Depends(has_permi("system:menu:add")),
    db: AsyncSession = Depends(get_db),
):
    await crud_menu.create_menu(db, body, current_user["user_name"])
    return AjaxResult.success()


@router.put("")
@log_operation("菜单管理", BusinessType.UPDATE)
async def update_menu(
    body: MenuUpdate,
    request: Request,
    current_user: dict = Depends(has_permi("system:menu:edit")),
    db: AsyncSession = Depends(get_db),
):
    if body.menu_id == body.parent_id:
        return AjaxResult.error(msg="修改菜单失败，上级菜单不能选择自己")
    await crud_menu.update_menu(db, body, current_user["user_name"])
    return AjaxResult.success()


@router.delete("/{menu_id}")
@log_operation("菜单管理", BusinessType.DELETE)
async def delete_menu(
    menu_id: int,
    request: Request,
    current_user: dict = Depends(has_permi("system:menu:remove")),
    db: AsyncSession = Depends(get_db),
):
    if await crud_menu.has_child(db, menu_id):
        return AjaxResult.error(msg="存在子菜单,不允许删除")
    await crud_menu.delete_menu(db, menu_id)
    return AjaxResult.success()


def _build_menu_tree(menus, parent_id: int) -> list[dict]:
    tree = []
    for m in menus:
        if m.parent_id == parent_id:
            node = {
                "id": m.menu_id,
                "label": m.menu_name,
                "children": _build_menu_tree(menus, m.menu_id),
            }
            tree.append(node)
    return tree
