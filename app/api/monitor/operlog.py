from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import BusinessType
from app.core.decorators import log_operation
from app.core.deps import has_permi
from app.core.response import AjaxResult, TableDataInfo
from app.crud.crud_oper_log import crud_oper_log
from app.db.session import get_db

router = APIRouter()


def _log_to_dict(log) -> dict:
    return {
        "operId": log.oper_id,
        "title": log.title,
        "businessType": log.business_type,
        "method": log.method,
        "requestMethod": log.request_method,
        "operatorType": log.operator_type,
        "operName": log.oper_name,
        "deptName": log.dept_name,
        "operUrl": log.oper_url,
        "operIp": log.oper_ip,
        "operLocation": log.oper_location,
        "operParam": log.oper_param,
        "jsonResult": log.json_result,
        "status": log.status,
        "errorMsg": log.error_msg,
        "operTime": log.oper_time.strftime("%Y-%m-%d %H:%M:%S") if log.oper_time else None,
        "costTime": log.cost_time,
    }


@router.get("/list")
async def list_oper_logs(
    current_user: dict = Depends(has_permi("monitor:operlog:list")),
    db: AsyncSession = Depends(get_db),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    title: str | None = Query(None),
    businessType: int | None = Query(None),
    operName: str | None = Query(None),
    status: int | None = Query(None),
    beginTime: str | None = Query(None, alias="params[beginTime]"),
    endTime: str | None = Query(None, alias="params[endTime]"),
):
    items, total = await crud_oper_log.get_oper_log_list(
        db, page_num=pageNum, page_size=pageSize,
        title=title, business_type=businessType,
        oper_name=operName, status=status,
        begin_time=beginTime, end_time=endTime,
    )
    return TableDataInfo(total=total, rows=[_log_to_dict(i) for i in items]).model_dump()


@router.post("/export")
@log_operation("操作日志", BusinessType.EXPORT)
async def export_oper_logs(
    request: Request,
    current_user: dict = Depends(has_permi("monitor:operlog:export")),
    db: AsyncSession = Depends(get_db),
):
    """Export operation log list to Excel."""
    from app.utils.excel_utils import export_to_excel
    items, _ = await crud_oper_log.get_oper_log_list(db, page_num=1, page_size=99999)
    data = [_log_to_dict(i) for i in items]
    return export_to_excel(
        headers=["操作编号", "系统模块", "操作类型", "请求方式", "操作人员", "操作地址", "操作状态", "操作时间", "消耗时间"],
        fields=["operId", "title", "businessType", "requestMethod", "operName", "operIp", "status", "operTime", "costTime"],
        data=data,
        sheet_name="操作日志",
    )


@router.delete("/{oper_ids}")
@log_operation("操作日志", BusinessType.DELETE)
async def delete_oper_logs(
    request: Request,
    oper_ids: str = Path(...),
    current_user: dict = Depends(has_permi("monitor:operlog:remove")),
    db: AsyncSession = Depends(get_db),
):
    ids = [int(i) for i in oper_ids.split(",") if i.strip()]
    await crud_oper_log.delete_by_ids(db, ids)
    return AjaxResult.success()


@router.delete("/clean")
@log_operation("操作日志", BusinessType.CLEAN)
async def clean_oper_logs(
    request: Request,
    current_user: dict = Depends(has_permi("monitor:operlog:remove")),
    db: AsyncSession = Depends(get_db),
):
    await crud_oper_log.clean(db)
    return AjaxResult.success()
