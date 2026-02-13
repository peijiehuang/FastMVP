import json

from fastapi import APIRouter, Depends, Path, Query, Request
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import SYS_CONFIG_KEY, BusinessType
from app.core.decorators import log_operation
from app.core.deps import get_current_user, has_permi
from app.core.redis import get_redis
from app.core.response import AjaxResult, TableDataInfo
from app.crud.crud_config import crud_config
from app.db.session import get_db
from app.schemas.sys_config import ConfigCreate, ConfigUpdate

router = APIRouter()


def _config_to_dict(c) -> dict:
    return {
        "configId": c.config_id,
        "configName": c.config_name,
        "configKey": c.config_key,
        "configValue": c.config_value,
        "configType": c.config_type,
        "createBy": c.create_by,
        "createTime": c.create_time.strftime("%Y-%m-%d %H:%M:%S") if c.create_time else None,
        "remark": c.remark,
    }


@router.get("/list")
async def list_configs(
    current_user: dict = Depends(has_permi("system:config:list")),
    db: AsyncSession = Depends(get_db),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    configName: str | None = Query(None),
    configKey: str | None = Query(None),
    configType: str | None = Query(None),
    beginTime: str | None = Query(None, alias="params[beginTime]"),
    endTime: str | None = Query(None, alias="params[endTime]"),
):
    items, total = await crud_config.get_config_list(
        db, page_num=pageNum, page_size=pageSize,
        config_name=configName, config_key=configKey, config_type=configType,
        begin_time=beginTime, end_time=endTime,
    )
    return TableDataInfo(total=total, rows=[_config_to_dict(i) for i in items]).model_dump()


@router.post("/export")
@log_operation("参数设置", BusinessType.EXPORT)
async def export_configs(
    request: Request,
    current_user: dict = Depends(has_permi("system:config:export")),
    db: AsyncSession = Depends(get_db),
):
    """Export config list to Excel."""
    from app.utils.excel_utils import export_to_excel
    items, _ = await crud_config.get_config_list(db, page_num=1, page_size=99999)
    data = [_config_to_dict(c) for c in items]
    return export_to_excel(
        headers=["参数编号", "参数名称", "参数键名", "参数键值", "系统内置", "备注"],
        fields=["configId", "configName", "configKey", "configValue", "configType", "remark"],
        data=data,
        sheet_name="参数数据",
    )


@router.get("/configKey/{config_key:path}")
async def get_config_by_key(
    config_key: str,
    redis_client: aioredis.Redis = Depends(get_redis),
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint: get config value by key (with Redis cache)."""
    cached = await redis_client.get(f"{SYS_CONFIG_KEY}{config_key}")
    if cached:
        return AjaxResult.success(msg=cached)

    cfg = await crud_config.get_by_key(db, config_key)
    if cfg:
        await redis_client.set(f"{SYS_CONFIG_KEY}{config_key}", cfg.config_value)
        return AjaxResult.success(msg=cfg.config_value)
    return AjaxResult.success(msg="")


@router.get("/{config_id}")
async def get_config(
    config_id: int,
    current_user: dict = Depends(has_permi("system:config:query")),
    db: AsyncSession = Depends(get_db),
):
    cfg = await crud_config.get(db, config_id)
    if not cfg:
        return AjaxResult.error(msg="参数不存在")
    return AjaxResult.success(data=_config_to_dict(cfg))


@router.post("")
@log_operation("参数设置", BusinessType.INSERT)
async def add_config(
    body: ConfigCreate,
    request: Request,
    current_user: dict = Depends(has_permi("system:config:add")),
    db: AsyncSession = Depends(get_db),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    existing = await crud_config.get_by_key(db, body.config_key)
    if existing:
        return AjaxResult.error(msg=f"参数键名'{body.config_key}'已存在")
    await crud_config.create_config(db, body, current_user["user_name"])
    await redis_client.set(f"{SYS_CONFIG_KEY}{body.config_key}", body.config_value)
    return AjaxResult.success()


@router.put("")
@log_operation("参数设置", BusinessType.UPDATE)
async def update_config(
    body: ConfigUpdate,
    request: Request,
    current_user: dict = Depends(has_permi("system:config:edit")),
    db: AsyncSession = Depends(get_db),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    cfg = await crud_config.update_config(db, body, current_user["user_name"])
    if cfg:
        await redis_client.set(f"{SYS_CONFIG_KEY}{cfg.config_key}", cfg.config_value)
    return AjaxResult.success()


@router.delete("/{config_ids}")
@log_operation("参数设置", BusinessType.DELETE)
async def delete_configs(
    request: Request,
    config_ids: str = Path(...),
    current_user: dict = Depends(has_permi("system:config:remove")),
    db: AsyncSession = Depends(get_db),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    ids = [int(i) for i in config_ids.split(",") if i.strip()]
    for cid in ids:
        cfg = await crud_config.get(db, cid)
        if cfg:
            await redis_client.delete(f"{SYS_CONFIG_KEY}{cfg.config_key}")
    await crud_config.delete_by_ids(db, ids)
    return AjaxResult.success()


@router.delete("/refreshCache")
async def refresh_cache(
    current_user: dict = Depends(has_permi("system:config:remove")),
    db: AsyncSession = Depends(get_db),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    """Rebuild all config caches."""
    async for key in redis_client.scan_iter(f"{SYS_CONFIG_KEY}*"):
        await redis_client.delete(key)
    items, _ = await crud_config.get_config_list(db, page_num=1, page_size=9999)
    for cfg in items:
        await redis_client.set(f"{SYS_CONFIG_KEY}{cfg.config_key}", cfg.config_value)
    return AjaxResult.success()
