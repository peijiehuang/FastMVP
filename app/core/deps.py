import json
from typing import Any

from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis.asyncio as aioredis

from app.config import settings
from app.core.constants import LOGIN_TOKEN_KEY, SUPER_ADMIN
from app.core.exceptions import AuthException, ForbiddenException
from app.core.redis import get_redis
from app.core.security import parse_token
from app.db.session import get_db

http_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    redis: aioredis.Redis = Depends(get_redis),
) -> dict:
    """Extract and validate token, load user info from Redis.

    Returns the LoginUser dict stored in Redis.
    """
    if not credentials:
        raise AuthException("未提供认证令牌")

    token = credentials.credentials
    user_key = parse_token(token)
    if not user_key:
        raise AuthException("令牌无效或已过期")

    user_json = await redis.get(f"{LOGIN_TOKEN_KEY}{user_key}")
    if not user_json:
        raise AuthException("登录已过期，请重新登录")

    # Refresh TTL
    await redis.expire(
        f"{LOGIN_TOKEN_KEY}{user_key}",
        settings.TOKEN_EXPIRE_MINUTES * 60,
    )

    return json.loads(user_json)


def has_permi(permission: str):
    """Permission check dependency factory."""

    async def check_permission(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        permissions = current_user.get("permissions", [])
        if "*:*:*" in permissions:
            return current_user
        if permission not in permissions:
            raise ForbiddenException(f"没有权限访问: {permission}")
        return current_user

    return check_permission


def has_role(role_key: str):
    """Role check dependency factory."""

    async def check_role(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        roles = current_user.get("roles", [])
        if SUPER_ADMIN in roles:
            return current_user
        if role_key not in roles:
            raise ForbiddenException(f"没有角色权限: {role_key}")
        return current_user

    return check_role
