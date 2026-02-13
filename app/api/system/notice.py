from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import BusinessType
from app.core.decorators import log_operation
from app.core.deps import has_permi
from app.core.response import AjaxResult, TableDataInfo
from app.crud.crud_notice import crud_notice
from app.db.session import get_db
from app.schemas.sys_notice import NoticeCreate, NoticeUpdate

router = APIRouter()


def _notice_to_dict(n) -> dict:
    return {
        "noticeId": n.notice_id,
        "noticeTitle": n.notice_title,
        "noticeType": n.notice_type,
        "noticeContent": n.notice_content,
        "status": n.status,
        "createBy": n.create_by,
        "createTime": n.create_time.strftime("%Y-%m-%d %H:%M:%S") if n.create_time else None,
        "updateBy": n.update_by,
        "updateTime": n.update_time.strftime("%Y-%m-%d %H:%M:%S") if n.update_time else None,
        "remark": n.remark,
    }


@router.get("/list")
async def list_notices(
    current_user: dict = Depends(has_permi("system:notice:list")),
    db: AsyncSession = Depends(get_db),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    noticeTitle: str | None = Query(None),
    noticeType: str | None = Query(None),
    createBy: str | None = Query(None),
):
    items, total = await crud_notice.get_notice_list(
        db, page_num=pageNum, page_size=pageSize,
        notice_title=noticeTitle, notice_type=noticeType, create_by=createBy,
    )
    return TableDataInfo(total=total, rows=[_notice_to_dict(i) for i in items]).model_dump()


@router.get("/{notice_id}")
async def get_notice(
    notice_id: int,
    current_user: dict = Depends(has_permi("system:notice:query")),
    db: AsyncSession = Depends(get_db),
):
    notice = await crud_notice.get(db, notice_id)
    if not notice:
        return AjaxResult.error(msg="通知公告不存在")
    return AjaxResult.success(data=_notice_to_dict(notice))


@router.post("")
@log_operation("通知公告", BusinessType.INSERT)
async def add_notice(
    body: NoticeCreate,
    request: Request,
    current_user: dict = Depends(has_permi("system:notice:add")),
    db: AsyncSession = Depends(get_db),
):
    await crud_notice.create_notice(db, body, current_user["user_name"])
    return AjaxResult.success()


@router.put("")
@log_operation("通知公告", BusinessType.UPDATE)
async def update_notice(
    body: NoticeUpdate,
    request: Request,
    current_user: dict = Depends(has_permi("system:notice:edit")),
    db: AsyncSession = Depends(get_db),
):
    await crud_notice.update_notice(db, body, current_user["user_name"])
    return AjaxResult.success()


@router.delete("/{notice_ids}")
@log_operation("通知公告", BusinessType.DELETE)
async def delete_notices(
    request: Request,
    notice_ids: str = Path(...),
    current_user: dict = Depends(has_permi("system:notice:remove")),
    db: AsyncSession = Depends(get_db),
):
    ids = [int(i) for i in notice_ids.split(",") if i.strip()]
    await crud_notice.delete_by_ids(db, ids)
    return AjaxResult.success()
