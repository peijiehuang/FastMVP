import json
from datetime import datetime

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.constants import (
    CAPTCHA_CODE_KEY, LOGIN_TOKEN_KEY, PWD_ERR_CNT_KEY, SUPER_ADMIN,
)
from app.core.exceptions import ServiceException
from app.core.security import (
    create_token, generate_uuid, get_password_hash, verify_password,
)
from app.models.sys_logininfor import SysLogininfor
from app.models.sys_menu import SysMenu
from app.models.sys_role import SysRole
from app.models.sys_user import SysUser
from app.models.associations import sys_user_role, sys_role_menu
from app.schemas.auth import LoginUser


async def login(
    username: str,
    password: str,
    code: str,
    captcha_uuid: str,
    login_ip: str,
    db: AsyncSession,
    redis: aioredis.Redis,
) -> str:
    """Authenticate user and return JWT token."""
    # 1. Validate captcha
    if settings.CAPTCHA_ENABLED:
        cache_key = f"{CAPTCHA_CODE_KEY}{captcha_uuid}"
        cached_code = await redis.get(cache_key)
        await redis.delete(cache_key)
        if not cached_code or cached_code.lower() != code.lower():
            raise ServiceException("验证码错误")

    # 2. Check account lock
    err_key = f"{PWD_ERR_CNT_KEY}{username}"
    err_count = await redis.get(err_key)
    if err_count and int(err_count) >= settings.MAX_RETRY_COUNT:
        raise ServiceException(
            f"密码错误次数过多，帐户已锁定{settings.LOCK_TIME_MINUTES}分钟"
        )

    # 3. Find user
    stmt = select(SysUser).where(
        SysUser.user_name == username,
        SysUser.del_flag == "0",
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        await _increment_login_error(redis, err_key)
        raise ServiceException("用户不存在/密码错误")

    # 4. Verify password
    if not verify_password(password, user.password):
        await _increment_login_error(redis, err_key)
        raise ServiceException("用户不存在/密码错误")

    # 5. Check status
    if user.status == "1":
        raise ServiceException("用户已停用")

    # Clear error count on success
    await redis.delete(err_key)

    # 6. Get permissions and roles
    permissions = await _get_user_permissions(user, db)
    role_keys = await _get_user_role_keys(user, db)

    # 7. Build LoginUser and cache in Redis
    token_key = generate_uuid()
    login_user = LoginUser(
        user_id=user.user_id,
        dept_id=user.dept_id,
        user_name=user.user_name,
        nick_name=user.nick_name,
        user_type=user.user_type,
        email=user.email,
        phonenumber=user.phonenumber,
        sex=user.sex,
        avatar=user.avatar,
        status=user.status,
        login_ip=login_ip,
        login_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        token_key=token_key,
        permissions=permissions,
        roles=role_keys,
        dept_name=user.dept.dept_name if user.dept else "",
    )

    await redis.setex(
        f"{LOGIN_TOKEN_KEY}{token_key}",
        settings.TOKEN_EXPIRE_MINUTES * 60,
        login_user.model_dump_json(),
    )

    # 8. Update user login info
    user.login_ip = login_ip
    user.login_date = datetime.now()
    await db.flush()

    # 9. Record login log
    await _record_login_log(db, username, login_ip, "0", "登录成功")

    # 10. Create JWT token
    return create_token(token_key)


async def logout(token_key: str, redis: aioredis.Redis):
    """Remove user token from Redis."""
    await redis.delete(f"{LOGIN_TOKEN_KEY}{token_key}")


async def get_user_info(current_user: dict, db: AsyncSession) -> dict:
    """Get user info for /getInfo endpoint."""
    user_id = current_user["user_id"]
    stmt = select(SysUser).where(SysUser.user_id == user_id, SysUser.del_flag == "0")
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise ServiceException("用户不存在")

    # Build user dict for response
    user_dict = {
        "userId": user.user_id,
        "deptId": user.dept_id,
        "userName": user.user_name,
        "nickName": user.nick_name,
        "email": user.email,
        "phonenumber": user.phonenumber,
        "sex": user.sex,
        "avatar": user.avatar,
        "status": user.status,
        "loginIp": user.login_ip,
        "loginDate": user.login_date.strftime("%Y-%m-%d %H:%M:%S") if user.login_date else None,
        "createTime": user.create_time.strftime("%Y-%m-%d %H:%M:%S") if user.create_time else None,
    }

    if user.dept:
        user_dict["dept"] = {
            "deptId": user.dept.dept_id,
            "deptName": user.dept.dept_name,
            "leader": user.dept.leader,
        }

    roles_set = set(current_user.get("roles", []))
    perms_set = set(current_user.get("permissions", []))

    return {
        "user": user_dict,
        "roles": list(roles_set),
        "permissions": list(perms_set),
    }


async def _get_user_permissions(user: SysUser, db: AsyncSession) -> list[str]:
    """Get all permission strings for a user."""
    # Admin gets all permissions
    if user.user_name == "admin":
        return ["*:*:*"]

    # Get role IDs for user
    stmt = select(sys_user_role.c.role_id).where(
        sys_user_role.c.user_id == user.user_id
    )
    result = await db.execute(stmt)
    role_ids = [row[0] for row in result.fetchall()]

    if not role_ids:
        return []

    # Get menu permissions through roles
    stmt = (
        select(SysMenu.perms)
        .join(sys_role_menu, sys_role_menu.c.menu_id == SysMenu.menu_id)
        .join(SysRole, SysRole.role_id == sys_role_menu.c.role_id)
        .where(
            sys_role_menu.c.role_id.in_(role_ids),
            SysRole.status == "0",
            SysRole.del_flag == "0",
            SysMenu.status == "0",
        )
    )
    result = await db.execute(stmt)
    perms = set()
    for row in result.fetchall():
        if row[0]:
            perms.add(row[0])

    return list(perms)


async def _get_user_role_keys(user: SysUser, db: AsyncSession) -> list[str]:
    """Get all role keys for a user."""
    if user.user_name == "admin":
        return [SUPER_ADMIN]

    stmt = (
        select(SysRole.role_key)
        .join(sys_user_role, sys_user_role.c.role_id == SysRole.role_id)
        .where(
            sys_user_role.c.user_id == user.user_id,
            SysRole.status == "0",
            SysRole.del_flag == "0",
        )
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.fetchall()]


async def _increment_login_error(redis: aioredis.Redis, err_key: str):
    """Increment failed login attempt counter."""
    count = await redis.incr(err_key)
    if count == 1:
        await redis.expire(err_key, settings.LOCK_TIME_MINUTES * 60)


async def _record_login_log(
    db: AsyncSession,
    user_name: str,
    ip: str,
    status: str,
    msg: str,
    browser: str = "",
    os: str = "",
):
    """Record a login/logout event in sys_logininfor."""
    from app.utils.ip_utils import get_ip_location

    log = SysLogininfor(
        user_name=user_name,
        ipaddr=ip,
        login_location=get_ip_location(ip),
        browser=browser,
        os=os,
        status=status,
        msg=msg,
        login_time=datetime.now(),
    )
    db.add(log)
    await db.flush()
