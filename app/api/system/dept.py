from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import BusinessType
from app.core.decorators import log_operation
from app.core.deps import get_current_user, has_permi
from app.core.response import AjaxResult
from app.crud.crud_dept import crud_dept
from app.db.session import get_db
from app.schemas.sys_dept import DeptCreate, DeptUpdate

router = APIRouter()


def _dept_to_dict(d) -> dict:
    return {
        "deptId": d.dept_id,
        "parentId": d.parent_id,
        "ancestors": d.ancestors,
        "deptName": d.dept_name,
        "orderNum": d.order_num,
        "leader": d.leader,
        "phone": d.phone,
        "email": d.email,
        "status": d.status,
        "createBy": d.create_by,
        "createTime": d.create_time.strftime("%Y-%m-%d %H:%M:%S") if d.create_time else None,
        "children": [],
    }


@router.get("/list")
async def list_depts(
    current_user: dict = Depends(has_permi("system:dept:list")),
    db: AsyncSession = Depends(get_db),
    deptName: str | None = Query(None),
    status: str | None = Query(None),
):
    depts = await crud_dept.get_all_depts(db, dept_name=deptName, status=status)
    return AjaxResult.success(data=[_dept_to_dict(d) for d in depts])


@router.get("/list/exclude/{dept_id}")
async def list_exclude(
    dept_id: int,
    current_user: dict = Depends(has_permi("system:dept:list")),
    db: AsyncSession = Depends(get_db),
):
    depts = await crud_dept.get_exclude_child(db, dept_id)
    return AjaxResult.success(data=[_dept_to_dict(d) for d in depts])


@router.get("/{dept_id}")
async def get_dept(
    dept_id: int,
    current_user: dict = Depends(has_permi("system:dept:query")),
    db: AsyncSession = Depends(get_db),
):
    dept = await crud_dept.get(db, dept_id)
    if not dept:
        return AjaxResult.error(msg="部门不存在")
    return AjaxResult.success(data=_dept_to_dict(dept))


@router.post("")
@log_operation("部门管理", BusinessType.INSERT)
async def add_dept(
    body: DeptCreate,
    request: Request,
    current_user: dict = Depends(has_permi("system:dept:add")),
    db: AsyncSession = Depends(get_db),
):
    await crud_dept.create_dept(db, body, current_user["user_name"])
    return AjaxResult.success()


@router.put("")
@log_operation("部门管理", BusinessType.UPDATE)
async def update_dept(
    body: DeptUpdate,
    request: Request,
    current_user: dict = Depends(has_permi("system:dept:edit")),
    db: AsyncSession = Depends(get_db),
):
    if body.dept_id == body.parent_id:
        return AjaxResult.error(msg="修改部门失败，上级部门不能是自己")
    await crud_dept.update_dept(db, body, current_user["user_name"])
    return AjaxResult.success()


@router.delete("/{dept_id}")
@log_operation("部门管理", BusinessType.DELETE)
async def delete_dept(
    dept_id: int,
    request: Request,
    current_user: dict = Depends(has_permi("system:dept:remove")),
    db: AsyncSession = Depends(get_db),
):
    success = await crud_dept.soft_delete(db, dept_id)
    if not success:
        return AjaxResult.error(msg="存在下级部门,不允许删除")
    return AjaxResult.success()
