import json

from fastapi import APIRouter, Depends, Path, Query, Request
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import SYS_DICT_KEY, BusinessType
from app.core.decorators import log_operation
from app.core.deps import get_current_user, has_permi
from app.core.redis import get_redis
from app.core.response import AjaxResult, TableDataInfo
from app.crud.crud_dict_type import crud_dict_type
from app.crud.crud_dict_data import crud_dict_data
from app.db.session import get_db
from app.schemas.sys_dict import DictTypeCreate, DictTypeUpdate

router = APIRouter()


def _dict_type_to_dict(dt) -> dict:
    return {
        "dictId": dt.dict_id,
        "dictName": dt.dict_name,
        "dictType": dt.dict_type,
        "status": dt.status,
        "createBy": dt.create_by,
        "createTime": dt.create_time.strftime("%Y-%m-%d %H:%M:%S") if dt.create_time else None,
        "remark": dt.remark,
    }


@router.get("/list")
async def list_dict_types(
    current_user: dict = Depends(has_permi("system:dict:list")),
    db: AsyncSession = Depends(get_db),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    dictName: str | None = Query(None),
    dictType: str | None = Query(None),
    status: str | None = Query(None),
    beginTime: str | None = Query(None, alias="params[beginTime]"),
    endTime: str | None = Query(None, alias="params[endTime]"),
):
    items, total = await crud_dict_type.get_dict_type_list(
        db, page_num=pageNum, page_size=pageSize,
        dict_name=dictName, dict_type=dictType, status=status,
        begin_time=beginTime, end_time=endTime,
    )
    return TableDataInfo(total=total, rows=[_dict_type_to_dict(i) for i in items]).model_dump()


@router.post("/export")
@log_operation("字典类型", BusinessType.EXPORT)
async def export_dict_types(
    request: Request,
    current_user: dict = Depends(has_permi("system:dict:export")),
    db: AsyncSession = Depends(get_db),
):
    """Export dict type list to Excel."""
    from app.utils.excel_utils import export_to_excel
    items, _ = await crud_dict_type.get_dict_type_list(db, page_num=1, page_size=99999)
    data = [_dict_type_to_dict(i) for i in items]
    return export_to_excel(
        headers=["字典编号", "字典名称", "字典类型", "状态", "备注"],
        fields=["dictId", "dictName", "dictType", "status", "remark"],
        data=data,
        sheet_name="字典类型数据",
    )


@router.get("/optionselect")
async def option_select(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await crud_dict_type.get_all_dict_types(db)
    return AjaxResult.success(data=[_dict_type_to_dict(i) for i in items])


@router.get("/{dict_id}")
async def get_dict_type(
    dict_id: int,
    current_user: dict = Depends(has_permi("system:dict:query")),
    db: AsyncSession = Depends(get_db),
):
    dt = await crud_dict_type.get(db, dict_id)
    if not dt:
        return AjaxResult.error(msg="字典类型不存在")
    return AjaxResult.success(data=_dict_type_to_dict(dt))


@router.post("")
@log_operation("字典类型", BusinessType.INSERT)
async def add_dict_type(
    body: DictTypeCreate,
    request: Request,
    current_user: dict = Depends(has_permi("system:dict:add")),
    db: AsyncSession = Depends(get_db),
):
    existing = await crud_dict_type.get_by_type(db, body.dict_type)
    if existing:
        return AjaxResult.error(msg=f"字典类型'{body.dict_type}'已存在")
    await crud_dict_type.create_dict_type(db, body, current_user["user_name"])
    return AjaxResult.success()


@router.put("")
@log_operation("字典类型", BusinessType.UPDATE)
async def update_dict_type(
    body: DictTypeUpdate,
    request: Request,
    current_user: dict = Depends(has_permi("system:dict:edit")),
    db: AsyncSession = Depends(get_db),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    await crud_dict_type.update_dict_type(db, body, current_user["user_name"])
    # Clear related dict data cache
    if body.dict_type:
        await redis_client.delete(f"{SYS_DICT_KEY}{body.dict_type}")
    return AjaxResult.success()


@router.delete("/{dict_ids}")
@log_operation("字典类型", BusinessType.DELETE)
async def delete_dict_types(
    request: Request,
    dict_ids: str = Path(...),
    current_user: dict = Depends(has_permi("system:dict:remove")),
    db: AsyncSession = Depends(get_db),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    ids = [int(i) for i in dict_ids.split(",") if i.strip()]
    # Clear cache for each type before deleting
    for did in ids:
        dt = await crud_dict_type.get(db, did)
        if dt:
            await redis_client.delete(f"{SYS_DICT_KEY}{dt.dict_type}")
    await crud_dict_type.delete_by_ids(db, ids)
    return AjaxResult.success()


@router.delete("/refreshCache")
async def refresh_cache(
    current_user: dict = Depends(has_permi("system:dict:remove")),
    db: AsyncSession = Depends(get_db),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    """Rebuild all dict caches."""
    # Delete all dict cache keys
    keys = []
    async for key in redis_client.scan_iter(f"{SYS_DICT_KEY}*"):
        keys.append(key)
    if keys:
        await redis_client.delete(*keys)

    # Rebuild cache
    all_types = await crud_dict_type.get_all_dict_types(db)
    for dt in all_types:
        data_list = await crud_dict_data.get_by_dict_type(db, dt.dict_type)
        cache_data = [
            {
                "dictCode": d.dict_code, "dictSort": d.dict_sort,
                "dictLabel": d.dict_label, "dictValue": d.dict_value,
                "dictType": d.dict_type, "cssClass": d.css_class,
                "listClass": d.list_class, "isDefault": d.is_default,
                "status": d.status,
            }
            for d in data_list
        ]
        await redis_client.set(f"{SYS_DICT_KEY}{dt.dict_type}", json.dumps(cache_data, ensure_ascii=False))
    return AjaxResult.success()
