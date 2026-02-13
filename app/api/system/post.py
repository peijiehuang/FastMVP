from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import BusinessType
from app.core.decorators import log_operation
from app.core.deps import get_current_user, has_permi
from app.core.response import AjaxResult, TableDataInfo
from app.crud.crud_post import crud_post
from app.db.session import get_db
from app.schemas.sys_post import PostCreate, PostUpdate

router = APIRouter()


def _post_to_dict(p) -> dict:
    return {
        "postId": p.post_id,
        "postCode": p.post_code,
        "postName": p.post_name,
        "postSort": p.post_sort,
        "status": p.status,
        "createBy": p.create_by,
        "createTime": p.create_time.strftime("%Y-%m-%d %H:%M:%S") if p.create_time else None,
        "remark": p.remark,
    }


@router.get("/list")
async def list_posts(
    current_user: dict = Depends(has_permi("system:post:list")),
    db: AsyncSession = Depends(get_db),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    postCode: str | None = Query(None),
    postName: str | None = Query(None),
    status: str | None = Query(None),
):
    posts, total = await crud_post.get_post_list(
        db, page_num=pageNum, page_size=pageSize,
        post_code=postCode, post_name=postName, status=status,
    )
    return TableDataInfo(total=total, rows=[_post_to_dict(p) for p in posts]).model_dump()


@router.post("/export")
@log_operation("岗位管理", BusinessType.EXPORT)
async def export_posts(
    request: Request,
    current_user: dict = Depends(has_permi("system:post:export")),
    db: AsyncSession = Depends(get_db),
):
    """Export post list to Excel."""
    from app.utils.excel_utils import export_to_excel
    posts, _ = await crud_post.get_post_list(db, page_num=1, page_size=99999)
    data = [_post_to_dict(p) for p in posts]
    return export_to_excel(
        headers=["岗位编号", "岗位编码", "岗位名称", "岗位排序", "状态"],
        fields=["postId", "postCode", "postName", "postSort", "status"],
        data=data,
        sheet_name="岗位数据",
    )


@router.get("/optionselect")
async def option_select(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    posts = await crud_post.get_all_posts(db)
    return AjaxResult.success(data=[_post_to_dict(p) for p in posts])


@router.get("/{post_id}")
async def get_post(
    post_id: int,
    current_user: dict = Depends(has_permi("system:post:query")),
    db: AsyncSession = Depends(get_db),
):
    post = await crud_post.get(db, post_id)
    if not post:
        return AjaxResult.error(msg="岗位不存在")
    return AjaxResult.success(data=_post_to_dict(post))


@router.post("")
@log_operation("岗位管理", BusinessType.INSERT)
async def add_post(
    body: PostCreate,
    request: Request,
    current_user: dict = Depends(has_permi("system:post:add")),
    db: AsyncSession = Depends(get_db),
):
    await crud_post.create_post(db, body, current_user["user_name"])
    return AjaxResult.success()


@router.put("")
@log_operation("岗位管理", BusinessType.UPDATE)
async def update_post(
    body: PostUpdate,
    request: Request,
    current_user: dict = Depends(has_permi("system:post:edit")),
    db: AsyncSession = Depends(get_db),
):
    await crud_post.update_post(db, body, current_user["user_name"])
    return AjaxResult.success()


@router.delete("/{post_ids}")
@log_operation("岗位管理", BusinessType.DELETE)
async def delete_posts(
    request: Request,
    post_ids: str = Path(...),
    current_user: dict = Depends(has_permi("system:post:remove")),
    db: AsyncSession = Depends(get_db),
):
    ids = [int(i) for i in post_ids.split(",") if i.strip()]
    await crud_post.delete_by_ids(db, ids)
    return AjaxResult.success()
