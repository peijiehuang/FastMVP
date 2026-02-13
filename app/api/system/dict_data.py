import json

from fastapi import APIRouter, Depends, Path, Query, Request
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import SYS_DICT_KEY, BusinessType
from app.core.decorators import log_operation
from app.core.deps import get_current_user, has_permi
from app.core.redis import get_redis
from app.core.response import AjaxResult, TableDataInfo
from app.crud.crud_dict_data import crud_dict_data
from app.db.session import get_db
from app.schemas.sys_dict import DictDataCreate, DictDataUpdate

router = APIRouter()


def _dict_data_to_dict(d) -> dict:
    return {
        "dictCode": d.dict_code,
        "dictSort": d.dict_sort,
        "dictLabel": d.dict_label,
        "dictValue": d.dict_value,
        "dictType": d.dict_type,
        "cssClass": d.css_class,
        "listClass": d.list_class,
        "isDefault": d.is_default,
        "status": d.status,
        "createBy": d.create_by,
        "createTime": d.create_time.strftime("%Y-%m-%d %H:%M:%S") if d.create_time else None,
        "remark": d.remark,
    }


@router.get("/list")
async def list_dict_data(
    current_user: dict = Depends(has_permi("system:dict:list")),
    db: AsyncSession = Depends(get_db),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    dictType: str | None = Query(None),
    dictLabel: str | None = Query(None),
    status: str | None = Query(None),
):
    items, total = await crud_dict_data.get_dict_data_list(
        db, page_num=pageNum, page_size=pageSize,
        dict_type=dictType, dict_label=dictLabel, status=status,
    )
    return TableDataInfo(total=total, rows=[_dict_data_to_dict(i) for i in items]).model_dump()


@router.post("/export")
@log_operation("字典数据", BusinessType.EXPORT)
async def export_dict_data(
    request: Request,
    current_user: dict = Depends(has_permi("system:dict:export")),
    db: AsyncSession = Depends(get_db),
):
    """Export dict data list to Excel."""
    from app.utils.excel_utils import export_to_excel
    items, _ = await crud_dict_data.get_dict_data_list(db, page_num=1, page_size=99999)
    data = [_dict_data_to_dict(i) for i in items]
    return export_to_excel(
        headers=["字典编码", "字典排序", "字典标签", "字典键值", "字典类型", "状态"],
        fields=["dictCode", "dictSort", "dictLabel", "dictValue", "dictType", "status"],
        data=data,
        sheet_name="字典数据",
    )


@router.get("/type/{dict_type}")
async def get_dict_data_by_type(
    dict_type: str,
    redis_client: aioredis.Redis = Depends(get_redis),
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint: get dict data by type (with Redis cache)."""
    cached = await redis_client.get(f"{SYS_DICT_KEY}{dict_type}")
    if cached:
        return AjaxResult.success(data=json.loads(cached))

    items = await crud_dict_data.get_by_dict_type(db, dict_type)
    data = [_dict_data_to_dict(i) for i in items]
    # Cache result
    await redis_client.set(
        f"{SYS_DICT_KEY}{dict_type}",
        json.dumps(data, ensure_ascii=False),
    )
    return AjaxResult.success(data=data)


@router.get("/{dict_code}")
async def get_dict_data(
    dict_code: int,
    current_user: dict = Depends(has_permi("system:dict:query")),
    db: AsyncSession = Depends(get_db),
):
    dd = await crud_dict_data.get(db, dict_code)
    if not dd:
        return AjaxResult.error(msg="字典数据不存在")
    return AjaxResult.success(data=_dict_data_to_dict(dd))


@router.post("")
@log_operation("字典数据", BusinessType.INSERT)
async def add_dict_data(
    body: DictDataCreate,
    request: Request,
    current_user: dict = Depends(has_permi("system:dict:add")),
    db: AsyncSession = Depends(get_db),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    await crud_dict_data.create_dict_data(db, body, current_user["user_name"])
    await redis_client.delete(f"{SYS_DICT_KEY}{body.dict_type}")
    return AjaxResult.success()


@router.put("")
@log_operation("字典数据", BusinessType.UPDATE)
async def update_dict_data(
    body: DictDataUpdate,
    request: Request,
    current_user: dict = Depends(has_permi("system:dict:edit")),
    db: AsyncSession = Depends(get_db),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    await crud_dict_data.update_dict_data(db, body, current_user["user_name"])
    if body.dict_type:
        await redis_client.delete(f"{SYS_DICT_KEY}{body.dict_type}")
    return AjaxResult.success()


@router.delete("/{dict_codes}")
@log_operation("字典数据", BusinessType.DELETE)
async def delete_dict_data(
    request: Request,
    dict_codes: str = Path(...),
    current_user: dict = Depends(has_permi("system:dict:remove")),
    db: AsyncSession = Depends(get_db),
    redis_client: aioredis.Redis = Depends(get_redis),
):
    codes = [int(i) for i in dict_codes.split(",") if i.strip()]
    # Clear cache for affected types
    for code in codes:
        dd = await crud_dict_data.get(db, code)
        if dd:
            await redis_client.delete(f"{SYS_DICT_KEY}{dd.dict_type}")
    await crud_dict_data.delete_by_ids(db, codes)
    return AjaxResult.success()
