from fastapi import APIRouter, Depends, Path, Query, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.constants import BusinessType
from app.core.decorators import log_operation
from app.core.deps import get_current_user, has_permi
from app.core.exceptions import ServiceException
from app.core.response import AjaxResult, TableDataInfo
from app.core.security import get_password_hash, verify_password
from app.crud.crud_role import crud_role
from app.crud.crud_user import crud_user
from app.db.session import get_db
from app.schemas.sys_user import (
    ChangeStatusBody, ResetPwdBody, UpdatePwdQuery, UserCreate, UserProfileUpdate, UserUpdate,
)

router = APIRouter()


def _user_to_dict(user) -> dict:
    """Convert SysUser model to dict for JSON serialization."""
    d = {
        "userId": user.user_id,
        "deptId": user.dept_id,
        "userName": user.user_name,
        "nickName": user.nick_name,
        "email": user.email,
        "phonenumber": user.phonenumber,
        "sex": user.sex,
        "avatar": user.avatar,
        "status": user.status,
        "delFlag": user.del_flag,
        "loginIp": user.login_ip,
        "loginDate": user.login_date.strftime("%Y-%m-%d %H:%M:%S") if user.login_date else None,
        "createBy": user.create_by,
        "createTime": user.create_time.strftime("%Y-%m-%d %H:%M:%S") if user.create_time else None,
        "updateBy": user.update_by,
        "updateTime": user.update_time.strftime("%Y-%m-%d %H:%M:%S") if user.update_time else None,
        "remark": user.remark,
    }
    if user.dept:
        d["dept"] = {
            "deptId": user.dept.dept_id,
            "parentId": user.dept.parent_id,
            "deptName": user.dept.dept_name,
            "orderNum": user.dept.order_num,
            "leader": user.dept.leader,
            "status": user.dept.status,
        }
    if hasattr(user, "roles") and user.roles:
        d["roles"] = [
            {
                "roleId": r.role_id,
                "roleName": r.role_name,
                "roleKey": r.role_key,
                "roleSort": r.role_sort,
                "dataScope": r.data_scope,
                "status": r.status,
            }
            for r in user.roles
        ]
    return d


# ===== Fixed route ordering: specific string paths BEFORE /{user_id} =====

@router.get("/list")
async def list_users(
    current_user: dict = Depends(has_permi("system:user:list")),
    db: AsyncSession = Depends(get_db),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    userName: str | None = Query(None),
    phonenumber: str | None = Query(None),
    status: str | None = Query(None),
    deptId: int | None = Query(None),
    beginTime: str | None = Query(None, alias="params[beginTime]"),
    endTime: str | None = Query(None, alias="params[endTime]"),
):
    users, total = await crud_user.get_user_list(
        db,
        page_num=pageNum,
        page_size=pageSize,
        user_name=userName,
        phonenumber=phonenumber,
        status=status,
        dept_id=deptId,
        begin_time=beginTime,
        end_time=endTime,
    )
    rows = [_user_to_dict(u) for u in users]
    return TableDataInfo(total=total, rows=rows).model_dump()


@router.post("/export")
@log_operation("用户管理", BusinessType.EXPORT)
async def export_users(
    request: Request,
    current_user: dict = Depends(has_permi("system:user:export")),
    db: AsyncSession = Depends(get_db),
):
    """Export user list to Excel."""
    from app.utils.excel_utils import export_to_excel
    users, _ = await crud_user.get_user_list(db, page_num=1, page_size=99999)
    data = [_user_to_dict(u) for u in users]
    return export_to_excel(
        headers=["用户编号", "登录名称", "用户昵称", "邮箱", "手机号码", "性别", "状态"],
        fields=["userId", "userName", "nickName", "email", "phonenumber", "sex", "status"],
        data=data,
        sheet_name="用户数据",
    )


@router.get("/deptTree")
async def dept_tree(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.crud.crud_dept import crud_dept
    depts = await crud_dept.get_all_depts(db)
    tree = _build_dept_tree(depts, 0)
    return AjaxResult.success(data=tree)


@router.get("/profile")
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await crud_user.get(db, current_user["user_id"])
    if not user:
        return AjaxResult.error(msg="用户不存在")
    role_group = ",".join(r.role_name for r in user.roles) if user.roles else ""
    post_group = ",".join(p.post_name for p in user.posts) if user.posts else ""
    return AjaxResult.success(
        data=_user_to_dict(user),
        roleGroup=role_group,
        postGroup=post_group,
    )


@router.put("/profile")
async def update_profile(
    body: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await crud_user.get(db, current_user["user_id"])
    if not user:
        return AjaxResult.error(msg="用户不存在")

    update_data = body.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(user, k, v)
    await db.flush()
    return AjaxResult.success()


@router.put("/profile/updatePwd")
async def update_pwd(
    oldPassword: str = Query(""),
    newPassword: str = Query(""),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await crud_user.get(db, current_user["user_id"])
    if not user:
        return AjaxResult.error(msg="用户不存在")
    if not verify_password(oldPassword, user.password):
        return AjaxResult.error(msg="修改密码失败，旧密码错误")
    if verify_password(newPassword, user.password):
        return AjaxResult.error(msg="新密码不能与旧密码相同")
    user.password = get_password_hash(newPassword)
    await db.flush()
    return AjaxResult.success()


@router.post("/profile/avatar")
async def upload_avatar(
    avatarfile: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    import os
    upload_dir = os.path.join(settings.UPLOAD_PATH, "avatar")
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(avatarfile.filename)[1] if avatarfile.filename else ".png"
    filename = f"{current_user['user_id']}{ext}"
    filepath = os.path.join(upload_dir, filename)

    content = await avatarfile.read()
    with open(filepath, "wb") as f:
        f.write(content)

    avatar_url = f"/profile/avatar/{filename}"
    await crud_user.update_avatar(db, current_user["user_id"], avatar_url)
    return AjaxResult.success(msg="上传成功", imgUrl=avatar_url)


@router.get("/authRole/{user_id}")
async def auth_role(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await crud_user.get(db, user_id)
    if not user:
        return AjaxResult.error(msg="用户不存在")
    roles = await crud_role.get_all_roles(db)
    user_role_ids = [r.role_id for r in user.roles] if user.roles else []
    return AjaxResult.success(
        user=_user_to_dict(user),
        roles=[
            {
                "roleId": r.role_id, "roleName": r.role_name, "roleKey": r.role_key,
                "roleSort": r.role_sort, "status": r.status,
                "flag": r.role_id in user_role_ids,
            }
            for r in roles if r.role_id != 1
        ],
    )


@router.put("/authRole")
@log_operation("用户管理", BusinessType.GRANT)
async def update_auth_role(
    request: Request,
    userId: int = Query(...),
    roleIds: str = Query(""),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import delete as sa_delete, insert as sa_insert
    from app.models.associations import sys_user_role

    role_ids = [int(i) for i in roleIds.split(",") if i.strip()]
    await db.execute(sa_delete(sys_user_role).where(sys_user_role.c.user_id == userId))
    if role_ids:
        await db.execute(
            sa_insert(sys_user_role),
            [{"user_id": userId, "role_id": rid} for rid in role_ids],
        )
    return AjaxResult.success()


@router.put("/resetPwd")
@log_operation("用户管理", BusinessType.UPDATE)
async def reset_pwd(
    body: ResetPwdBody,
    request: Request,
    current_user: dict = Depends(has_permi("system:user:resetPwd")),
    db: AsyncSession = Depends(get_db),
):
    password_hash = get_password_hash(body.password)
    await crud_user.reset_password(db, body.user_id, password_hash, current_user["user_name"])
    return AjaxResult.success()


@router.put("/changeStatus")
@log_operation("用户管理", BusinessType.UPDATE)
async def change_status(
    body: ChangeStatusBody,
    request: Request,
    current_user: dict = Depends(has_permi("system:user:edit")),
    db: AsyncSession = Depends(get_db),
):
    await crud_user.update_status(db, body.user_id, body.status, current_user["user_name"])
    return AjaxResult.success()


@router.get("/")
async def get_user_add_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get info needed for add user form (posts + roles)."""
    from app.crud.crud_post import crud_post
    posts = await crud_post.get_all_posts(db)
    roles = await crud_role.get_all_roles(db)
    return AjaxResult.success(
        posts=[{"postId": p.post_id, "postCode": p.post_code, "postName": p.post_name, "postSort": p.post_sort, "status": p.status} for p in posts],
        roles=[{"roleId": r.role_id, "roleName": r.role_name, "roleKey": r.role_key, "roleSort": r.role_sort, "status": r.status} for r in roles if r.role_id != 1],
    )


# ===== Path parameter routes LAST =====

@router.get("/{user_id}")
async def get_user(
    user_id: int,
    current_user: dict = Depends(has_permi("system:user:query")),
    db: AsyncSession = Depends(get_db),
):
    from app.crud.crud_post import crud_post
    user = await crud_user.get(db, user_id)
    if not user:
        return AjaxResult.error(msg="用户不存在")

    posts = await crud_post.get_all_posts(db)
    roles = await crud_role.get_all_roles(db)
    post_ids = [p.post_id for p in user.posts] if user.posts else []
    role_ids = [r.role_id for r in user.roles] if user.roles else []

    return AjaxResult.success(
        data=_user_to_dict(user),
        posts=[{"postId": p.post_id, "postCode": p.post_code, "postName": p.post_name, "postSort": p.post_sort, "status": p.status} for p in posts],
        roles=[{"roleId": r.role_id, "roleName": r.role_name, "roleKey": r.role_key, "roleSort": r.role_sort, "status": r.status} for r in roles if r.role_id != 1],
        postIds=post_ids,
        roleIds=role_ids,
    )


@router.post("")
@log_operation("用户管理", BusinessType.INSERT)
async def add_user(
    body: UserCreate,
    request: Request,
    current_user: dict = Depends(has_permi("system:user:add")),
    db: AsyncSession = Depends(get_db),
):
    existing = await crud_user.get_by_username(db, body.user_name)
    if existing:
        return AjaxResult.error(msg=f"新增用户'{body.user_name}'失败，登录账号已存在")

    password = body.password or "123456"
    password_hash = get_password_hash(password)
    await crud_user.create_user(db, body, password_hash, current_user["user_name"])
    return AjaxResult.success()


@router.put("")
@log_operation("用户管理", BusinessType.UPDATE)
async def update_user(
    body: UserUpdate,
    request: Request,
    current_user: dict = Depends(has_permi("system:user:edit")),
    db: AsyncSession = Depends(get_db),
):
    await crud_user.update_user(db, body, current_user["user_name"])
    return AjaxResult.success()


@router.delete("/{user_ids}")
@log_operation("用户管理", BusinessType.DELETE)
async def delete_users(
    request: Request,
    user_ids: str = Path(...),
    current_user: dict = Depends(has_permi("system:user:remove")),
    db: AsyncSession = Depends(get_db),
):
    ids = [int(i) for i in user_ids.split(",") if i.strip()]
    if current_user["user_id"] in ids:
        return AjaxResult.error(msg="当前用户不能删除")
    await crud_user.soft_delete(db, ids)
    return AjaxResult.success()


def _build_dept_tree(depts, parent_id: int) -> list[dict]:
    tree = []
    for d in depts:
        if d.parent_id == parent_id:
            node = {"id": d.dept_id, "label": d.dept_name, "children": _build_dept_tree(depts, d.dept_id)}
            tree.append(node)
    return tree
