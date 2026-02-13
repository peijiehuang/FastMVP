from fastapi import APIRouter, Depends, Path, Query, Request
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import PWD_ERR_CNT_KEY, BusinessType
from app.core.decorators import log_operation
from app.core.deps import has_permi
from app.core.redis import get_redis
from app.core.response import AjaxResult, TableDataInfo
from app.crud.crud_logininfor import crud_logininfor
from app.db.session import get_db

router = APIRouter()


def _log_to_dict(log) -> dict:
    return {
        "infoId": log.info_id,
        "userName": log.user_name,
        "ipaddr": log.ipaddr,
        "loginLocation": log.login_location,
        "browser": log.browser,
        "os": log.os,
        "status": log.status,
        "msg": log.msg,
        "loginTime": log.login_time.strftime("%Y-%m-%d %H:%M:%S") if log.login_time else None,
    }


@router.get("/list")
async def list_logininfor(
    current_user: dict = Depends(has_permi("monitor:logininfor:list")),
    db: AsyncSession = Depends(get_db),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    userName: str | None = Query(None),
    ipaddr: str | None = Query(None),
    status: str | None = Query(None),
    beginTime: str | None = Query(None, alias="params[beginTime]"),
    endTime: str | None = Query(None, alias="params[endTime]"),
):
    items, total = await crud_logininfor.get_logininfor_list(
        db, page_num=pageNum, page_size=pageSize,
        user_name=userName, ipaddr=ipaddr, status=status,
        begin_time=beginTime, end_time=endTime,
    )
    return TableDataInfo(total=total, rows=[_log_to_dict(i) for i in items]).model_dump()


@router.post("/export")
@log_operation("登录日志", BusinessType.EXPORT)
async def export_logininfor(
    request: Request,
    current_user: dict = Depends(has_permi("monitor:logininfor:export")),
    db: AsyncSession = Depends(get_db),
):
    """Export login info list to Excel."""
    from app.utils.excel_utils import export_to_excel
    items, _ = await crud_logininfor.get_logininfor_list(db, page_num=1, page_size=99999)
    data = [_log_to_dict(i) for i in items]
    return export_to_excel(
        headers=["访问编号", "用户名称", "登录地址", "登录地点", "浏览器", "操作系统", "登录状态", "操作信息", "登录时间"],
        fields=["infoId", "userName", "ipaddr", "loginLocation", "browser", "os", "status", "msg", "loginTime"],
        data=data,
        sheet_name="登录日志",
    )


@router.delete("/{info_ids}")
@log_operation("登录日志", BusinessType.DELETE)
async def delete_logininfor(
    request: Request,
    info_ids: str = Path(...),
    current_user: dict = Depends(has_permi("monitor:logininfor:remove")),
    db: AsyncSession = Depends(get_db),
):
    ids = [int(i) for i in info_ids.split(",") if i.strip()]
    await crud_logininfor.delete_by_ids(db, ids)
    return AjaxResult.success()


@router.delete("/clean")
@log_operation("登录日志", BusinessType.CLEAN)
async def clean_logininfor(
    request: Request,
    current_user: dict = Depends(has_permi("monitor:logininfor:remove")),
    db: AsyncSession = Depends(get_db),
):
    await crud_logininfor.clean(db)
    return AjaxResult.success()


@router.get("/unlock/{user_name}")
async def unlock_user(
    user_name: str,
    current_user: dict = Depends(has_permi("monitor:logininfor:unlock")),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    await redis_client.delete(f"{PWD_ERR_CNT_KEY}{user_name}")
    return AjaxResult.success(msg=f"解锁用户'{user_name}'成功")
