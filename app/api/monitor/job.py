from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import BusinessType
from app.core.decorators import log_operation
from app.core.deps import has_permi
from app.core.response import AjaxResult, TableDataInfo
from app.crud.crud_job import crud_job
from app.db.session import get_db
from app.schemas.sys_job import JobCreate, JobUpdate, JobStatusChange, JobRun
from app.services.job_service import (
    add_job_to_scheduler, remove_job_from_scheduler,
    run_job_once, get_next_fire_time,
)

router = APIRouter()


def _job_to_dict(j) -> dict:
    next_time = get_next_fire_time(j.job_id)
    return {
        "jobId": j.job_id,
        "jobName": j.job_name,
        "jobGroup": j.job_group,
        "invokeTarget": j.invoke_target,
        "cronExpression": j.cron_expression,
        "misfirePolicy": j.misfire_policy,
        "concurrent": j.concurrent,
        "status": j.status,
        "createBy": j.create_by,
        "createTime": j.create_time.strftime("%Y-%m-%d %H:%M:%S") if j.create_time else None,
        "updateTime": j.update_time.strftime("%Y-%m-%d %H:%M:%S") if j.update_time else None,
        "remark": j.remark,
        "nextValidTime": next_time.strftime("%Y-%m-%d %H:%M:%S") if next_time else None,
    }


@router.get("/list")
async def list_jobs(
    current_user: dict = Depends(has_permi("monitor:job:list")),
    db: AsyncSession = Depends(get_db),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    jobName: str | None = Query(None),
    jobGroup: str | None = Query(None),
    status: str | None = Query(None),
):
    items, total = await crud_job.get_job_list(
        db, page_num=pageNum, page_size=pageSize,
        job_name=jobName, job_group=jobGroup, status=status,
    )
    return TableDataInfo(total=total, rows=[_job_to_dict(j) for j in items]).model_dump()


@router.post("/export")
@log_operation("定时任务", BusinessType.EXPORT)
async def export_jobs(
    request: Request,
    current_user: dict = Depends(has_permi("monitor:job:export")),
    db: AsyncSession = Depends(get_db),
):
    from app.utils.excel_utils import export_to_excel
    items, _ = await crud_job.get_job_list(db, page_num=1, page_size=99999)
    data = [_job_to_dict(j) for j in items]
    return export_to_excel(
        headers=["任务编号", "任务名称", "任务组名", "调用目标", "cron表达式", "状态"],
        fields=["jobId", "jobName", "jobGroup", "invokeTarget", "cronExpression", "status"],
        data=data,
        sheet_name="定时任务",
    )


# --- changeStatus and run MUST be before /{job_id} ---

@router.put("/changeStatus")
@log_operation("定时任务", BusinessType.UPDATE)
async def change_job_status(
    body: JobStatusChange,
    request: Request,
    current_user: dict = Depends(has_permi("monitor:job:changeStatus")),
    db: AsyncSession = Depends(get_db),
):
    job = await crud_job.get(db, body.job_id)
    if not job:
        return AjaxResult.error(msg="任务不存在")
    await crud_job.update_job(
        db, JobUpdate(job_id=body.job_id, status=body.status),
        current_user.get("user_name", "admin"),
    )
    if body.status == "0":
        job = await crud_job.get(db, body.job_id)
        add_job_to_scheduler(job)
    else:
        remove_job_from_scheduler(body.job_id)
    return AjaxResult.success()


@router.put("/run")
@log_operation("定时任务", BusinessType.UPDATE)
async def run_job(
    body: JobRun,
    request: Request,
    current_user: dict = Depends(has_permi("monitor:job:changeStatus")),
    db: AsyncSession = Depends(get_db),
):
    job = await crud_job.get(db, body.job_id)
    if not job:
        return AjaxResult.error(msg="任务不存在")
    await run_job_once(job)
    return AjaxResult.success()


@router.get("/{job_id}")
async def get_job(
    job_id: int,
    current_user: dict = Depends(has_permi("monitor:job:query")),
    db: AsyncSession = Depends(get_db),
):
    job = await crud_job.get(db, job_id)
    if not job:
        return AjaxResult.error(msg="任务不存在")
    return AjaxResult.success(data=_job_to_dict(job))


@router.post("")
@log_operation("定时任务", BusinessType.INSERT)
async def add_job(
    body: JobCreate,
    request: Request,
    current_user: dict = Depends(has_permi("monitor:job:add")),
    db: AsyncSession = Depends(get_db),
):
    job = await crud_job.create_job(db, body, current_user.get("user_name", "admin"))
    if job.status == "0":
        add_job_to_scheduler(job)
    return AjaxResult.success()


@router.put("")
@log_operation("定时任务", BusinessType.UPDATE)
async def update_job(
    body: JobUpdate,
    request: Request,
    current_user: dict = Depends(has_permi("monitor:job:edit")),
    db: AsyncSession = Depends(get_db),
):
    job = await crud_job.update_job(db, body, current_user.get("user_name", "admin"))
    if job:
        remove_job_from_scheduler(job.job_id)
        if job.status == "0":
            add_job_to_scheduler(job)
    return AjaxResult.success()


@router.delete("/{job_ids}")
@log_operation("定时任务", BusinessType.DELETE)
async def delete_jobs(
    request: Request,
    job_ids: str = Path(...),
    current_user: dict = Depends(has_permi("monitor:job:remove")),
    db: AsyncSession = Depends(get_db),
):
    ids = [int(i) for i in job_ids.split(",") if i.strip()]
    for jid in ids:
        remove_job_from_scheduler(jid)
    await crud_job.delete_by_ids(db, ids)
    return AjaxResult.success()
