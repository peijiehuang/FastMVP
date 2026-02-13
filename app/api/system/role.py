from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import BusinessType
from app.core.decorators import log_operation
from app.core.deps import get_current_user, has_permi
from app.core.response import AjaxResult, TableDataInfo
from app.crud.crud_role import crud_role
from app.db.session import get_db
from app.schemas.sys_role import (
    AuthUserBody, RoleChangeStatus, RoleCreate, RoleDataScope, RoleUpdate,
)

router = APIRouter()


def _role_to_dict(role) -> dict:
    return {
        "roleId": role.role_id,
        "roleName": role.role_name,
        "roleKey": role.role_key,
        "roleSort": role.role_sort,
        "dataScope": role.data_scope,
        "menuCheckStrictly": role.menu_check_strictly,
        "deptCheckStrictly": role.dept_check_strictly,
        "status": role.status,
        "delFlag": role.del_flag,
        "createBy": role.create_by,
        "createTime": role.create_time.strftime("%Y-%m-%d %H:%M:%S") if role.create_time else None,
        "remark": role.remark,
    }


def _user_to_dict(user) -> dict:
    return {
        "userId": user.user_id,
        "userName": user.user_name,
        "nickName": user.nick_name,
        "email": user.email,
        "phonenumber": user.phonenumber,
        "status": user.status,
        "createTime": user.create_time.strftime("%Y-%m-%d %H:%M:%S") if user.create_time else None,
    }


@router.get("/list")
async def list_roles(
    current_user: dict = Depends(has_permi("system:role:list")),
    db: AsyncSession = Depends(get_db),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    roleName: str | None = Query(None),
    roleKey: str | None = Query(None),
    status: str | None = Query(None),
    beginTime: str | None = Query(None, alias="params[beginTime]"),
    endTime: str | None = Query(None, alias="params[endTime]"),
):
    roles, total = await crud_role.get_role_list(
        db,
        page_num=pageNum,
        page_size=pageSize,
        role_name=roleName,
        role_key=roleKey,
        status=status,
        begin_time=beginTime,
        end_time=endTime,
    )
    rows = [_role_to_dict(r) for r in roles]
    return TableDataInfo(total=total, rows=rows).model_dump()


@router.post("/export")
@log_operation("角色管理", BusinessType.EXPORT)
async def export_roles(
    request: Request,
    current_user: dict = Depends(has_permi("system:role:export")),
    db: AsyncSession = Depends(get_db),
):
    """Export role list to Excel."""
    from app.utils.excel_utils import export_to_excel
    roles, _ = await crud_role.get_role_list(db, page_num=1, page_size=99999)
    data = [_role_to_dict(r) for r in roles]
    return export_to_excel(
        headers=["角色编号", "角色名称", "权限字符", "显示顺序", "数据范围", "状态"],
        fields=["roleId", "roleName", "roleKey", "roleSort", "dataScope", "status"],
        data=data,
        sheet_name="角色数据",
    )


@router.get("/optionselect")
async def option_select(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    roles = await crud_role.get_all_roles(db)
    return AjaxResult.success(data=[_role_to_dict(r) for r in roles])


@router.get("/{role_id}")
async def get_role(
    role_id: int,
    current_user: dict = Depends(has_permi("system:role:query")),
    db: AsyncSession = Depends(get_db),
):
    role = await crud_role.get(db, role_id)
    if not role:
        return AjaxResult.error(msg="角色不存在")
    return AjaxResult.success(data=_role_to_dict(role))


@router.post("")
@log_operation("角色管理", BusinessType.INSERT)
async def add_role(
    body: RoleCreate,
    request: Request,
    current_user: dict = Depends(has_permi("system:role:add")),
    db: AsyncSession = Depends(get_db),
):
    await crud_role.create_role(db, body, current_user["user_name"])
    return AjaxResult.success()


@router.put("")
@log_operation("角色管理", BusinessType.UPDATE)
async def update_role(
    body: RoleUpdate,
    request: Request,
    current_user: dict = Depends(has_permi("system:role:edit")),
    db: AsyncSession = Depends(get_db),
):
    await crud_role.update_role(db, body, current_user["user_name"])
    return AjaxResult.success()


@router.put("/dataScope")
@log_operation("角色管理", BusinessType.GRANT)
async def set_data_scope(
    body: RoleDataScope,
    request: Request,
    current_user: dict = Depends(has_permi("system:role:edit")),
    db: AsyncSession = Depends(get_db),
):
    await crud_role.update_data_scope(
        db, body.role_id, body.data_scope, body.dept_ids, current_user["user_name"]
    )
    return AjaxResult.success()


@router.put("/changeStatus")
@log_operation("角色管理", BusinessType.UPDATE)
async def change_status(
    body: RoleChangeStatus,
    request: Request,
    current_user: dict = Depends(has_permi("system:role:edit")),
    db: AsyncSession = Depends(get_db),
):
    await crud_role.update_status(db, body.role_id, body.status, current_user["user_name"])
    return AjaxResult.success()


@router.delete("/{role_ids}")
@log_operation("角色管理", BusinessType.DELETE)
async def delete_roles(
    request: Request,
    role_ids: str = Path(...),
    current_user: dict = Depends(has_permi("system:role:remove")),
    db: AsyncSession = Depends(get_db),
):
    ids = [int(i) for i in role_ids.split(",") if i.strip()]
    await crud_role.soft_delete(db, ids)
    return AjaxResult.success()


@router.get("/authUser/allocatedList")
async def allocated_list(
    roleId: int = Query(...),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    userName: str | None = Query(None),
    phonenumber: str | None = Query(None),
    current_user: dict = Depends(has_permi("system:role:list")),
    db: AsyncSession = Depends(get_db),
):
    users, total = await crud_role.get_allocated_users(
        db, roleId, page_num=pageNum, page_size=pageSize,
        user_name=userName, phonenumber=phonenumber,
    )
    return TableDataInfo(total=total, rows=[_user_to_dict(u) for u in users]).model_dump()


@router.get("/authUser/unallocatedList")
async def unallocated_list(
    roleId: int = Query(...),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    userName: str | None = Query(None),
    phonenumber: str | None = Query(None),
    current_user: dict = Depends(has_permi("system:role:list")),
    db: AsyncSession = Depends(get_db),
):
    users, total = await crud_role.get_unallocated_users(
        db, roleId, page_num=pageNum, page_size=pageSize,
        user_name=userName, phonenumber=phonenumber,
    )
    return TableDataInfo(total=total, rows=[_user_to_dict(u) for u in users]).model_dump()


@router.put("/authUser/cancel")
@log_operation("角色管理", BusinessType.GRANT)
async def cancel_auth(
    body: AuthUserBody,
    request: Request,
    current_user: dict = Depends(has_permi("system:role:edit")),
    db: AsyncSession = Depends(get_db),
):
    await crud_role.cancel_auth_user(db, body.user_id, body.role_id)
    return AjaxResult.success()


@router.put("/authUser/cancelAll")
@log_operation("角色管理", BusinessType.GRANT)
async def cancel_all_auth(
    request: Request,
    roleId: int = Query(...),
    userIds: str = Query(""),
    current_user: dict = Depends(has_permi("system:role:edit")),
    db: AsyncSession = Depends(get_db),
):
    ids = [int(i) for i in userIds.split(",") if i.strip()]
    await crud_role.cancel_auth_users(db, roleId, ids)
    return AjaxResult.success()


@router.put("/authUser/selectAll")
@log_operation("角色管理", BusinessType.GRANT)
async def select_all_auth(
    request: Request,
    roleId: int = Query(...),
    userIds: str = Query(""),
    current_user: dict = Depends(has_permi("system:role:edit")),
    db: AsyncSession = Depends(get_db),
):
    ids = [int(i) for i in userIds.split(",") if i.strip()]
    await crud_role.select_auth_users(db, roleId, ids)
    return AjaxResult.success()


@router.get("/deptTree/{role_id}")
async def role_dept_tree(
    role_id: int,
    current_user: dict = Depends(has_permi("system:role:query")),
    db: AsyncSession = Depends(get_db),
):
    from app.crud.crud_dept import crud_dept
    from sqlalchemy import select
    from app.models.associations import sys_role_dept

    depts = await crud_dept.get_all_depts(db)

    # Get checked dept IDs for this role
    result = await db.execute(
        select(sys_role_dept.c.dept_id).where(sys_role_dept.c.role_id == role_id)
    )
    checked_keys = [row[0] for row in result.fetchall()]

    tree = _build_dept_tree_select(depts, 0)
    return AjaxResult.success(checkedKeys=checked_keys, depts=tree)


def _build_dept_tree_select(depts, parent_id: int) -> list[dict]:
    tree = []
    for d in depts:
        if d.parent_id == parent_id:
            node = {"id": d.dept_id, "label": d.dept_name, "children": _build_dept_tree_select(depts, d.dept_id)}
            tree.append(node)
    return tree
