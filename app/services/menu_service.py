from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MenuType
from app.models.sys_menu import SysMenu
from app.models.sys_role import SysRole
from app.models.associations import sys_user_role, sys_role_menu


async def get_routers(user_id: int, is_admin: bool, db: AsyncSession) -> list[dict]:
    """Build Vue router tree for the current user."""
    if is_admin:
        stmt = (
            select(SysMenu)
            .where(
                SysMenu.menu_type.in_([MenuType.DIRECTORY, MenuType.MENU]),
                SysMenu.status == "0",
            )
            .order_by(SysMenu.parent_id, SysMenu.order_num)
        )
    else:
        stmt = (
            select(SysMenu)
            .join(sys_role_menu, sys_role_menu.c.menu_id == SysMenu.menu_id)
            .join(SysRole, SysRole.role_id == sys_role_menu.c.role_id)
            .join(sys_user_role, sys_user_role.c.role_id == SysRole.role_id)
            .where(
                sys_user_role.c.user_id == user_id,
                SysMenu.menu_type.in_([MenuType.DIRECTORY, MenuType.MENU]),
                SysMenu.status == "0",
                SysRole.status == "0",
            )
            .order_by(SysMenu.parent_id, SysMenu.order_num)
            .distinct()
        )

    result = await db.execute(stmt)
    menus = result.scalars().all()
    return _build_router_tree(menus, 0)


def _build_router_tree(menus: list[SysMenu], parent_id: int) -> list[dict]:
    """Recursively build Vue Router compatible tree."""
    tree = []
    children_menus = [m for m in menus if m.parent_id == parent_id]

    for menu in children_menus:
        router = _build_router_node(menu, menus)
        tree.append(router)

    return tree


def _build_router_node(menu: SysMenu, all_menus: list[SysMenu]) -> dict:
    """Convert a SysMenu to Vue Router format matching RuoYi frontend expectations."""
    children = _build_router_tree(all_menus, menu.menu_id)

    router: dict = {
        "name": _get_route_name(menu),
        "path": _get_router_path(menu),
        "hidden": menu.visible == "1",
        "component": _get_component(menu),
        "meta": {
            "title": menu.menu_name,
            "icon": menu.icon,
            "noCache": menu.is_cache == 1,
        },
    }

    if menu.query:
        router["query"] = menu.query

    if menu.is_frame == 0:
        router["meta"]["link"] = menu.path

    if children:
        router["alwaysShow"] = True
        router["redirect"] = "noRedirect"
        router["children"] = children
    elif menu.parent_id == 0 and menu.menu_type == MenuType.DIRECTORY:
        # Top-level directory with no children
        router["alwaysShow"] = True
        router["redirect"] = "noRedirect"
        router["children"] = []
    elif menu.parent_id == 0 and menu.menu_type == MenuType.MENU:
        # Top-level menu item, wrap with Layout
        child = {
            "path": menu.path,
            "component": menu.component or "",
            "name": menu.path.capitalize() if menu.path else "",
            "meta": {
                "title": menu.menu_name,
                "icon": menu.icon,
                "noCache": menu.is_cache == 1,
            },
        }
        if menu.query:
            child["query"] = menu.query
        if menu.is_frame == 0:
            child["meta"]["link"] = menu.path
        router["path"] = "/"
        router["hidden"] = menu.visible == "1"
        router["component"] = "Layout"
        router["redirect"] = "noRedirect" if menu.visible == "0" else ""
        router["children"] = [child]
        router.pop("name", None)
        router["meta"] = {"title": menu.menu_name, "icon": menu.icon}

    return router


def _get_route_name(menu: SysMenu) -> str:
    """Get the route name, capitalize first letter."""
    if menu.route_name:
        return menu.route_name
    path = menu.path or ""
    return path[:1].upper() + path[1:] if path else ""


def _get_router_path(menu: SysMenu) -> str:
    """Get the router path."""
    path = menu.path or ""
    # Top-level directory, add / prefix
    if menu.parent_id == 0 and menu.menu_type == MenuType.DIRECTORY and menu.is_frame == 1:
        path = "/" + path
    return path


def _get_component(menu: SysMenu) -> str:
    """Get the component path."""
    component = "Layout"
    if menu.component:
        component = menu.component
    elif menu.parent_id != 0 and _is_inner_link(menu):
        component = "InnerLink"
    elif menu.parent_id != 0 and menu.menu_type == MenuType.DIRECTORY:
        component = "ParentView"
    elif menu.parent_id == 0:
        component = "Layout"
    return component


def _is_inner_link(menu: SysMenu) -> bool:
    """Check if menu is an inner link (iframe)."""
    return menu.is_frame == 0 and bool(menu.path)
