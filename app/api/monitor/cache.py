from fastapi import APIRouter, Depends, Path
import redis.asyncio as aioredis

from app.core.deps import has_permi
from app.core.redis import get_redis
from app.core.response import AjaxResult

router = APIRouter()

# Predefined cache names (matching RuoYi frontend expectations)
CACHE_NAMES = [
    {"cacheName": "login_tokens", "remark": "用户信息"},
    {"cacheName": "sys_config", "remark": "配置信息"},
    {"cacheName": "sys_dict", "remark": "数据字典"},
    {"cacheName": "captcha_codes", "remark": "验证码"},
    {"cacheName": "repeat_submit", "remark": "防重提交"},
    {"cacheName": "pwd_err_cnt", "remark": "密码错误次数"},
]


@router.get("")
async def get_cache_info(
    current_user: dict = Depends(has_permi("monitor:cache:list")),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    """Get Redis server info."""
    info = await redis_client.info()
    db_size = await redis_client.dbsize()

    command_stats = []
    cmd_info = await redis_client.info("commandstats")
    for key, val in cmd_info.items():
        if key.startswith("cmdstat_"):
            cmd_name = key.replace("cmdstat_", "")
            command_stats.append({
                "name": cmd_name,
                "value": str(val.get("calls", 0)),
            })

    return AjaxResult.success(data={
        "info": info,
        "dbSize": db_size,
        "commandStats": command_stats,
    })


@router.get("/getNames")
async def get_cache_names(
    current_user: dict = Depends(has_permi("monitor:cache:list")),
):
    return AjaxResult.success(data=CACHE_NAMES)


@router.get("/getKeys/{cache_name}")
async def get_cache_keys(
    cache_name: str,
    current_user: dict = Depends(has_permi("monitor:cache:list")),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    keys = []
    async for key in redis_client.scan_iter(f"{cache_name}:*"):
        keys.append(key)
    return AjaxResult.success(data=keys)


@router.get("/getValue/{cache_name}/{cache_key:path}")
async def get_cache_value(
    cache_name: str,
    cache_key: str,
    current_user: dict = Depends(has_permi("monitor:cache:list")),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    value = await redis_client.get(cache_key)
    return AjaxResult.success(data={
        "cacheName": cache_name,
        "cacheKey": cache_key,
        "cacheValue": value or "",
        "remark": "",
    })


@router.delete("/clearCacheName/{cache_name}")
async def clear_cache_name(
    cache_name: str,
    current_user: dict = Depends(has_permi("monitor:cache:list")),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    keys = []
    async for key in redis_client.scan_iter(f"{cache_name}:*"):
        keys.append(key)
    if keys:
        await redis_client.delete(*keys)
    return AjaxResult.success()


@router.delete("/clearCacheKey/{cache_key:path}")
async def clear_cache_key(
    cache_key: str,
    current_user: dict = Depends(has_permi("monitor:cache:list")),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    await redis_client.delete(cache_key)
    return AjaxResult.success()


@router.delete("/clearCacheAll")
async def clear_cache_all(
    current_user: dict = Depends(has_permi("monitor:cache:list")),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    await redis_client.flushdb()
    return AjaxResult.success()
