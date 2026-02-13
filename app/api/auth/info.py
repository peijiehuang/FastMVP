from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import SUPER_ADMIN
from app.core.deps import get_current_user
from app.core.response import AjaxResult
from app.db.session import get_db
from app.services import auth_service, menu_service

router = APIRouter(tags=["认证管理"])


@router.get("/getInfo")
async def get_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user info, roles, and permissions."""
    info = await auth_service.get_user_info(current_user, db)
    return AjaxResult.success(
        user=info["user"],
        roles=info["roles"],
        permissions=info["permissions"],
    )


@router.get("/getRouters")
async def get_routers(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get Vue router tree for the current user."""
    user_id = current_user["user_id"]
    is_admin = SUPER_ADMIN in current_user.get("roles", [])
    routers = await menu_service.get_routers(user_id, is_admin, db)
    return AjaxResult.success(data=routers)
