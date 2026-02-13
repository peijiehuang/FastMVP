from sqlalchemy import BigInteger, String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, AuditMixin


class GenTable(Base, AuditMixin):
    __tablename__ = "gen_table"

    table_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    table_name: Mapped[str] = mapped_column(String(200), default="", server_default="")
    table_comment: Mapped[str] = mapped_column(String(500), default="", server_default="")
    sub_table_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sub_table_fk_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    class_name: Mapped[str] = mapped_column(String(100), default="", server_default="")
    tpl_category: Mapped[str] = mapped_column(String(200), default="crud", server_default="crud")
    tpl_web_type: Mapped[str] = mapped_column(String(30), default="", server_default="")
    package_name: Mapped[str] = mapped_column(String(100), default="", server_default="")
    module_name: Mapped[str] = mapped_column(String(30), default="", server_default="")
    business_name: Mapped[str] = mapped_column(String(30), default="", server_default="")
    function_name: Mapped[str] = mapped_column(String(50), default="", server_default="")
    function_author: Mapped[str] = mapped_column(String(50), default="", server_default="")
    gen_type: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
    gen_path: Mapped[str] = mapped_column(String(200), default="/", server_default="/")
    options: Mapped[str | None] = mapped_column(String(1000), nullable=True)


class GenTableColumn(Base, AuditMixin):
    __tablename__ = "gen_table_column"

    column_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    table_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    column_name: Mapped[str] = mapped_column(String(200), default="", server_default="")
    column_comment: Mapped[str] = mapped_column(String(500), default="", server_default="")
    column_type: Mapped[str] = mapped_column(String(100), default="", server_default="")
    python_type: Mapped[str] = mapped_column(String(500), default="", server_default="")
    python_field: Mapped[str] = mapped_column(String(200), default="", server_default="")
    is_pk: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
    is_increment: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
    is_required: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
    is_insert: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
    is_edit: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
    is_list: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
    is_query: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
    query_type: Mapped[str] = mapped_column(String(200), default="EQ", server_default="EQ")
    html_type: Mapped[str] = mapped_column(String(200), default="", server_default="")
    dict_type: Mapped[str] = mapped_column(String(200), default="", server_default="")
    sort: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
