from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi.responses import StreamingResponse
import io
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import has_permi
from app.core.response import AjaxResult, TableDataInfo
from app.db.session import get_db
from app.services import codegen_service

router = APIRouter()


def _table_to_dict(t) -> dict:
    return {
        "tableId": t.table_id,
        "tableName": t.table_name,
        "tableComment": t.table_comment,
        "className": t.class_name,
        "tplCategory": t.tpl_category,
        "moduleName": t.module_name,
        "businessName": t.business_name,
        "functionName": t.function_name,
        "functionAuthor": t.function_author,
        "genType": t.gen_type,
        "genPath": t.gen_path,
        "options": t.options,
        "createBy": t.create_by,
        "createTime": t.create_time.strftime("%Y-%m-%d %H:%M:%S") if t.create_time else None,
        "updateBy": t.update_by,
        "updateTime": t.update_time.strftime("%Y-%m-%d %H:%M:%S") if t.update_time else None,
        "remark": t.remark,
    }


def _column_to_dict(c) -> dict:
    return {
        "columnId": c.column_id,
        "tableId": c.table_id,
        "columnName": c.column_name,
        "columnComment": c.column_comment,
        "columnType": c.column_type,
        "pythonType": c.python_type,
        "pythonField": c.python_field,
        "isPk": c.is_pk,
        "isIncrement": c.is_increment,
        "isRequired": c.is_required,
        "isInsert": c.is_insert,
        "isEdit": c.is_edit,
        "isList": c.is_list,
        "isQuery": c.is_query,
        "queryType": c.query_type,
        "htmlType": c.html_type,
        "dictType": c.dict_type,
        "sort": c.sort,
    }


@router.get("/list")
async def list_gen_tables(
    current_user: dict = Depends(has_permi("tool:gen:list")),
    db: AsyncSession = Depends(get_db),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    tableName: str | None = Query(None),
    tableComment: str | None = Query(None),
    beginTime: str | None = Query(None, alias="params[beginTime]"),
    endTime: str | None = Query(None, alias="params[endTime]"),
):
    items, total = await codegen_service.get_gen_table_list(
        db, page_num=pageNum, page_size=pageSize,
        table_name=tableName, table_comment=tableComment,
        begin_time=beginTime, end_time=endTime,
    )
    return TableDataInfo(total=total, rows=[_table_to_dict(i) for i in items]).model_dump()


@router.get("/db/list")
async def list_db_tables(
    current_user: dict = Depends(has_permi("tool:gen:list")),
    db: AsyncSession = Depends(get_db),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    tableName: str | None = Query(None),
    tableComment: str | None = Query(None),
):
    items, total = await codegen_service.get_db_table_list(
        db, page_num=pageNum, page_size=pageSize,
        table_name=tableName, table_comment=tableComment,
    )
    return TableDataInfo(total=total, rows=items).model_dump()


@router.get("/batchGenCode")
async def batch_gen_code(
    tables: str = Query(""),
    current_user: dict = Depends(has_permi("tool:gen:code")),
    db: AsyncSession = Depends(get_db),
):
    table_names = [t.strip() for t in tables.split(",") if t.strip()]
    if not table_names:
        return AjaxResult.error(msg="请选择要生成的表")
    zip_bytes = await codegen_service.generate_code_zip(db, table_names)
    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=ruoyi.zip"},
    )


@router.get("/genCode/{table_name}")
async def gen_code(
    table_name: str,
    current_user: dict = Depends(has_permi("tool:gen:code")),
    db: AsyncSession = Depends(get_db),
):
    zip_bytes = await codegen_service.generate_code_zip(db, [table_name])
    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={table_name}.zip"},
    )


@router.get("/synchDb/{table_name}")
async def synch_db(
    table_name: str,
    current_user: dict = Depends(has_permi("tool:gen:edit")),
    db: AsyncSession = Depends(get_db),
):
    await codegen_service.synch_db(db, table_name)
    await db.commit()
    return AjaxResult.success()


@router.get("/{table_id}")
async def get_gen_table(
    table_id: int,
    current_user: dict = Depends(has_permi("tool:gen:query")),
    db: AsyncSession = Depends(get_db),
):
    table, columns = await codegen_service.get_table_with_columns(db, table_id)
    if not table:
        return AjaxResult.error(msg="表不存在")
    return AjaxResult.success(data={
        "info": _table_to_dict(table),
        "rows": [_column_to_dict(c) for c in columns],
    })


@router.get("/preview/{table_id}")
async def preview(
    table_id: int,
    current_user: dict = Depends(has_permi("tool:gen:preview")),
    db: AsyncSession = Depends(get_db),
):
    code = await codegen_service.preview_code(db, table_id)
    return AjaxResult.success(data=code)


@router.post("/importTable")
async def import_table(
    tables: str = Query(""),
    current_user: dict = Depends(has_permi("tool:gen:import")),
    db: AsyncSession = Depends(get_db),
):
    table_names = [t.strip() for t in tables.split(",") if t.strip()]
    if not table_names:
        return AjaxResult.error(msg="请选择要导入的表")
    await codegen_service.import_tables(db, table_names, current_user["user_name"])
    return AjaxResult.success()


@router.put("")
async def update_gen_table(
    request: Request,
    current_user: dict = Depends(has_permi("tool:gen:edit")),
    db: AsyncSession = Depends(get_db),
):
    body = await request.json()
    table_data = body
    columns_data = body.get("columns", [])
    await codegen_service.update_gen_table(db, table_data, columns_data, current_user["user_name"])
    return AjaxResult.success()


@router.delete("/{table_ids}")
async def delete_gen_tables(
    table_ids: str = Path(...),
    current_user: dict = Depends(has_permi("tool:gen:remove")),
    db: AsyncSession = Depends(get_db),
):
    ids = [int(i) for i in table_ids.split(",") if i.strip()]
    await codegen_service.delete_gen_tables(db, ids)
    return AjaxResult.success()
