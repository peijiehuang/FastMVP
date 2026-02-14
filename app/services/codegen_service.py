import os
import re
from datetime import datetime
from typing import Sequence

from sqlalchemy import text, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gen_table import GenTable, GenTableColumn


# MySQL type -> Python type mapping
TYPE_MAP = {
    "bigint": "int",
    "int": "int",
    "integer": "int",
    "tinyint": "int",
    "smallint": "int",
    "mediumint": "int",
    "float": "float",
    "double": "float",
    "decimal": "float",
    "varchar": "str",
    "char": "str",
    "text": "str",
    "longtext": "str",
    "mediumtext": "str",
    "tinytext": "str",
    "datetime": "datetime",
    "date": "date",
    "timestamp": "datetime",
    "blob": "bytes",
    "longblob": "bytes",
}


def _to_camel_case(snake_str: str) -> str:
    """Convert snake_case to CamelCase."""
    return "".join(x.capitalize() for x in snake_str.split("_"))


def _to_snake_field(name: str) -> str:
    """Ensure snake_case for Python field name."""
    return name.lower()


def _get_python_type(col_type: str) -> str:
    """Map MySQL column type to Python type."""
    base = re.sub(r"\(.*\)", "", col_type).strip().lower()
    return TYPE_MAP.get(base, "str")


async def get_db_table_list(
    db: AsyncSession,
    *,
    page_num: int = 1,
    page_size: int = 10,
    table_name: str | None = None,
    table_comment: str | None = None,
) -> tuple[list[dict], int]:
    """Get tables from INFORMATION_SCHEMA that are not yet imported."""
    # Get already imported tables
    imported = await db.execute(select(GenTable.table_name))
    imported_names = {row[0] for row in imported.fetchall()}

    sql = """
        SELECT table_name, table_comment, create_time, update_time
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
        AND table_name NOT LIKE 'gen_%'
    """
    params = {}
    if table_name:
        sql += " AND table_name LIKE :tn"
        params["tn"] = f"%{table_name}%"
    if table_comment:
        sql += " AND table_comment LIKE :tc"
        params["tc"] = f"%{table_comment}%"
    sql += " ORDER BY create_time DESC"

    result = await db.execute(text(sql), params)
    rows = result.fetchall()

    tables = []
    for r in rows:
        if r[0] not in imported_names:
            tables.append({
                "tableName": r[0],
                "tableComment": r[1] or "",
                "createTime": r[2].strftime("%Y-%m-%d %H:%M:%S") if r[2] else None,
                "updateTime": r[3].strftime("%Y-%m-%d %H:%M:%S") if r[3] else None,
            })

    total = len(tables)
    start = (page_num - 1) * page_size
    return tables[start:start + page_size], total


async def import_tables(
    db: AsyncSession, table_names: list[str], create_by: str
):
    """Import table metadata from INFORMATION_SCHEMA into gen_table."""
    for tname in table_names:
        # Get table info
        result = await db.execute(text(
            "SELECT table_name, table_comment FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = :tn"
        ), {"tn": tname})
        row = result.fetchone()
        if not row:
            continue

        gen_table = GenTable(
            table_name=row[0],
            table_comment=row[1] or "",
            class_name=_to_camel_case(row[0]),
            module_name=row[0].replace("_", ""),
            business_name=row[0].split("_")[-1] if "_" in row[0] else row[0],
            function_name=row[1] or row[0],
            function_author="admin",
            create_by=create_by,
        )
        db.add(gen_table)
        await db.flush()

        # Get columns
        col_result = await db.execute(text(
            "SELECT column_name, column_comment, column_type, column_key, extra, is_nullable "
            "FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = :tn "
            "ORDER BY ordinal_position"
        ), {"tn": tname})

        for idx, col in enumerate(col_result.fetchall()):
            col_name, col_comment, col_type, col_key, extra, nullable = col
            is_pk = "1" if col_key == "PRI" else "0"
            is_increment = "1" if extra and "auto_increment" in extra else "0"
            python_type = _get_python_type(col_type)
            python_field = _to_snake_field(col_name)

            gen_col = GenTableColumn(
                table_id=gen_table.table_id,
                column_name=col_name,
                column_comment=col_comment or "",
                column_type=col_type,
                python_type=python_type,
                python_field=python_field,
                is_pk=is_pk,
                is_increment=is_increment,
                is_required="0" if nullable == "YES" or is_pk == "1" else "1",
                is_insert="1" if is_pk == "0" else "0",
                is_edit="1" if is_pk == "0" else "0",
                is_list="1",
                is_query="1" if idx < 5 else "0",
                query_type="EQ",
                html_type=_guess_html_type(col_name, col_type),
                sort=idx,
                create_by=create_by,
            )
            db.add(gen_col)

    await db.flush()


def _guess_html_type(col_name: str, col_type: str) -> str:
    base = re.sub(r"\(.*\)", "", col_type).strip().lower()
    if base in ("text", "longtext", "mediumtext"):
        return "textarea"
    if "time" in col_name or "date" in col_name:
        return "datetime"
    if col_name.endswith("_type") or col_name.endswith("_status") or col_name == "status" or col_name == "sex":
        return "select"
    return "input"


async def get_gen_table_list(
    db: AsyncSession,
    *,
    page_num: int = 1,
    page_size: int = 10,
    table_name: str | None = None,
    table_comment: str | None = None,
    begin_time: str | None = None,
    end_time: str | None = None,
) -> tuple[Sequence[GenTable], int]:
    query = select(GenTable)
    if table_name:
        query = query.where(GenTable.table_name.like(f"%{table_name}%"))
    if table_comment:
        query = query.where(GenTable.table_comment.like(f"%{table_comment}%"))
    if begin_time:
        query = query.where(GenTable.create_time >= begin_time)
    if end_time:
        query = query.where(GenTable.create_time <= end_time)
    query = query.order_by(GenTable.table_id.desc())

    from app.crud.base import CRUDBase
    crud = CRUDBase(GenTable)
    return await crud.get_list(db, query=query, page_num=page_num, page_size=page_size)


async def get_table_with_columns(
    db: AsyncSession, table_id: int
) -> tuple[GenTable | None, Sequence[GenTableColumn]]:
    table = await db.get(GenTable, table_id)
    if not table:
        return None, []
    result = await db.execute(
        select(GenTableColumn)
        .where(GenTableColumn.table_id == table_id)
        .order_by(GenTableColumn.sort)
    )
    columns = result.scalars().all()
    return table, columns


async def update_gen_table(
    db: AsyncSession, table_data: dict, columns_data: list[dict], update_by: str
):
    table_id = table_data.get("tableId")
    table = await db.get(GenTable, table_id)
    if not table:
        return

    for key in ("tableName", "tableComment", "className", "functionAuthor",
                "moduleName", "businessName", "functionName", "tplCategory",
                "tplWebType", "genType", "genPath", "options", "remark"):
        snake = re.sub(r'([A-Z])', r'_\1', key).lower()
        if key in table_data and hasattr(table, snake):
            setattr(table, snake, table_data[key])
    table.update_by = update_by
    table.update_time = datetime.now()

    for col_data in columns_data:
        col_id = col_data.get("columnId")
        if not col_id:
            continue
        col = await db.get(GenTableColumn, col_id)
        if not col:
            continue
        for key in ("columnComment", "pythonType", "pythonField",
                    "isInsert", "isEdit", "isList", "isQuery",
                    "isRequired", "queryType", "htmlType", "dictType"):
            snake = re.sub(r'([A-Z])', r'_\1', key).lower()
            if key in col_data and hasattr(col, snake):
                setattr(col, snake, col_data[key])

    await db.flush()


async def delete_gen_tables(db: AsyncSession, table_ids: list[int]):
    for tid in table_ids:
        await db.execute(delete(GenTableColumn).where(GenTableColumn.table_id == tid))
    await db.execute(delete(GenTable).where(GenTable.table_id.in_(table_ids)))
    await db.flush()


async def preview_code(db: AsyncSession, table_id: int) -> dict[str, str]:
    """Generate preview code from a gen_table entry."""
    from jinja2 import Environment, FileSystemLoader
    import os

    table, columns = await get_table_with_columns(db, table_id)
    if not table:
        return {}

    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
    if not os.path.exists(template_dir):
        os.makedirs(template_dir, exist_ok=True)

    # Build context
    pk_column = next((c for c in columns if c.is_pk == "1"), columns[0] if columns else None)
    context = {
        "table": table,
        "columns": columns,
        "pk_column": pk_column,
        "class_name": table.class_name,
        "module_name": table.module_name,
        "business_name": table.business_name,
        "function_name": table.function_name,
        "author": table.function_author,
        "table_name": table.table_name,
        "datetime": datetime.now().strftime("%Y-%m-%d"),
    }

    result = {}
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=False)

    # Key format must be "vm/python/<name>.python.vm" for RuoYi frontend highlight.js
    for tpl_name in ("model.py.j2", "schema.py.j2", "crud.py.j2", "api.py.j2"):
        try:
            tpl = env.get_template(tpl_name)
            code = tpl.render(**context)
            base_name = tpl_name.replace(".py.j2", "")
            result[f"vm/python/{base_name}.python.vm"] = code
        except Exception:
            base_name = tpl_name.replace(".py.j2", "")
            result[f"vm/python/{base_name}.python.vm"] = f"# Template '{tpl_name}' not found or error"

    return result


async def synch_db(db: AsyncSession, table_name: str):
    """Re-sync column info from database for an existing gen_table."""
    # Find the gen_table
    result = await db.execute(
        select(GenTable).where(GenTable.table_name == table_name)
    )
    table = result.scalar_one_or_none()
    if not table:
        return

    # Get current columns from database
    col_result = await db.execute(text(
        "SELECT column_name, column_comment, column_type, column_key, extra, is_nullable "
        "FROM information_schema.columns "
        "WHERE table_schema = DATABASE() AND table_name = :tn "
        "ORDER BY ordinal_position"
    ), {"tn": table_name})
    db_columns = col_result.fetchall()

    # Get existing gen_table_column records
    existing_result = await db.execute(
        select(GenTableColumn).where(GenTableColumn.table_id == table.table_id)
    )
    existing_cols = {c.column_name: c for c in existing_result.scalars().all()}

    for idx, col in enumerate(db_columns):
        col_name, col_comment, col_type, col_key, extra, nullable = col
        if col_name in existing_cols:
            # Update existing
            ec = existing_cols[col_name]
            ec.column_comment = col_comment or ""
            ec.column_type = col_type
            ec.python_type = _get_python_type(col_type)
            ec.is_pk = "1" if col_key == "PRI" else "0"
            ec.sort = idx
            del existing_cols[col_name]
        else:
            # New column
            is_pk = "1" if col_key == "PRI" else "0"
            gen_col = GenTableColumn(
                table_id=table.table_id,
                column_name=col_name,
                column_comment=col_comment or "",
                column_type=col_type,
                python_type=_get_python_type(col_type),
                python_field=_to_snake_field(col_name),
                is_pk=is_pk,
                is_increment="1" if extra and "auto_increment" in extra else "0",
                is_required="0" if nullable == "YES" or is_pk == "1" else "1",
                is_insert="1" if is_pk == "0" else "0",
                is_edit="1" if is_pk == "0" else "0",
                is_list="1",
                is_query="0",
                query_type="EQ",
                html_type=_guess_html_type(col_name, col_type),
                sort=idx,
                create_by="admin",
            )
            db.add(gen_col)

    # Delete columns that no longer exist in database
    for old_col in existing_cols.values():
        await db.delete(old_col)

    await db.flush()


async def generate_code_zip(db: AsyncSession, table_names: list[str]) -> bytes:
    """Generate code for tables and return as zip bytes."""
    import io
    import zipfile
    from jinja2 import Environment, FileSystemLoader

    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=False)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for tname in table_names:
            result = await db.execute(
                select(GenTable).where(GenTable.table_name == tname)
            )
            table = result.scalar_one_or_none()
            if not table:
                continue

            col_result = await db.execute(
                select(GenTableColumn)
                .where(GenTableColumn.table_id == table.table_id)
                .order_by(GenTableColumn.sort)
            )
            columns = col_result.scalars().all()

            pk_column = next((c for c in columns if c.is_pk == "1"), columns[0] if columns else None)
            context = {
                "table": table,
                "columns": columns,
                "pk_column": pk_column,
                "class_name": table.class_name,
                "module_name": table.module_name,
                "business_name": table.business_name,
                "function_name": table.function_name,
                "author": table.function_author,
                "table_name": table.table_name,
                "datetime": datetime.now().strftime("%Y-%m-%d"),
            }

            for tpl_name in ("model.py.j2", "schema.py.j2", "crud.py.j2", "api.py.j2"):
                try:
                    tpl = env.get_template(tpl_name)
                    code = tpl.render(**context)
                    file_name = tpl_name.replace(".j2", "")
                    zf.writestr(f"{tname}/{file_name}", code)
                except Exception:
                    pass

    return buf.getvalue()
