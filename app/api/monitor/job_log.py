from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import BusinessType
from app.core.decorators import log_operation
from app.core.deps import has_permi
from app.core.response import AjaxResult, TableDataInfo
from app.crud.crud_job_log import crud_job_log
from app.db.session import get_db

router = APIRouter()


def _log_to_dict(log) -> dict:
    return {
        "jobLogId": log.job_log_id,
        "jobName": log.job_name,
        "jobGroup": log.job_group,
        "invokeTarget": log.invoke_target,
        "jobMessage": log.job_message,
        "status": log.status,
        "exceptionInfo": log.exception_info,
        "createTime": log.create_time.strftime("%Y-%m-%d %H:%M:%S") if log.create_time else None,
    }


@router.get("/list")
async def list_job_logs(
    current_user: dict = Depends(has_permi("monitor:job:list")),
    db: AsyncSession = Depends(get_db),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    jobName: str | None = Query(None),
    jobGroup: str | None = Query(None),
    status: str | None = Query(None),
    beginTime: str | None = Query(None, alias="params[beginTime]"),
    endTime: str | None = Query(None, alias="params[endTime]"),
):
    items, total = await crud_job_log.get_job_log_list(
        db, page_num=pageNum, page_size=pageSize,
        job_name=jobName, job_group=jobGroup, status=status,
        begin_time=beginTime, end_time=endTime,
    )
    return TableDataInfo(total=total, rows=[_log_to_dict(i) for i in items]).model_dump()


@router.post("/export")
@log_operation("调度日志", BusinessType.EXPORT)
async def export_job_logs(
    request: Request,
    current_user: dict = Depends(has_permi("monitor:job:export")),
    db: AsyncSession = Depends(get_db),
):
    from app.utils.excel_utils import export_to_excel
    items, _ = await crud_job_log.get_job_log_list(db, page_num=1, page_size=99999)
    data = [_log_to_dict(i) for i in items]
    return export_to_excel(
        headers=["日志编号", "任务名称", "任务组名", "调用目标", "日志信息", "执行状态", "异常信息", "执行时间"],
        fields=["jobLogId", "jobName", "jobGroup", "invokeTarget", "jobMessage", "status", "exceptionInfo", "createTime"],
        data=data,
        sheet_name="调度日志",
    )


# clean MUST be before /{job_log_ids}
@router.delete("/clean")
@log_operation("调度日志", BusinessType.CLEAN)
async def clean_job_logs(
    request: Request,
    current_user: dict = Depends(has_permi("monitor:job:remove")),
    db: AsyncSession = Depends(get_db),
):
    await crud_job_log.clean(db)
    return AjaxResult.success()


@router.delete("/{job_log_ids}")
@log_operation("调度日志", BusinessType.DELETE)
async def delete_job_logs(
    request: Request,
    job_log_ids: str = Path(...),
    current_user: dict = Depends(has_permi("monitor:job:remove")),
    db: AsyncSession = Depends(get_db),
):
    ids = [int(i) for i in job_log_ids.split(",") if i.strip()]
    await crud_job_log.delete_by_ids(db, ids)
    return AjaxResult.success()
