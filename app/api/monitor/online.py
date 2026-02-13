import json

from fastapi import APIRouter, Depends, Query, Request
import redis.asyncio as aioredis

from app.core.constants import LOGIN_TOKEN_KEY, BusinessType
from app.core.decorators import log_operation
from app.core.deps import has_permi
from app.core.redis import get_redis
from app.core.response import AjaxResult, TableDataInfo

router = APIRouter()


@router.get("/list")
async def list_online_users(
    current_user: dict = Depends(has_permi("monitor:online:list")),
    redis_client: aioredis.Redis = Depends(get_redis),
    ipaddr: str | None = Query(None),
    userName: str | None = Query(None),
):
    """List all online users by scanning Redis login tokens."""
    online_users = []
    async for key in redis_client.scan_iter(f"{LOGIN_TOKEN_KEY}*"):
        user_json = await redis_client.get(key)
        if not user_json:
            continue
        user_data = json.loads(user_json)

        if ipaddr and ipaddr not in user_data.get("login_ip", ""):
            continue
        if userName and userName not in user_data.get("user_name", ""):
            continue

        online_users.append({
            "tokenId": user_data.get("token_key", ""),
            "userName": user_data.get("user_name", ""),
            "ipaddr": user_data.get("login_ip", ""),
            "loginLocation": "",
            "browser": "",
            "os": "",
            "deptName": user_data.get("dept_name", ""),
            "loginTime": user_data.get("login_time", ""),
        })

    total = len(online_users)
    return TableDataInfo(total=total, rows=online_users).model_dump()


@router.delete("/{token_id}")
@log_operation("在线用户", BusinessType.FORCE)
async def force_logout(
    token_id: str,
    request: Request,
    current_user: dict = Depends(has_permi("monitor:online:forceLogout")),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    """Force logout a user by deleting their token from Redis."""
    await redis_client.delete(f"{LOGIN_TOKEN_KEY}{token_id}")
    return AjaxResult.success()
