from sqlalchemy import BigInteger, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, AuditMixin


class SysDictData(Base, AuditMixin):
    __tablename__ = "sys_dict_data"

    dict_code: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    dict_sort: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    dict_label: Mapped[str] = mapped_column(String(100), default="", server_default="")
    dict_value: Mapped[str] = mapped_column(String(100), default="", server_default="")
    dict_type: Mapped[str] = mapped_column(String(100), default="", server_default="")
    css_class: Mapped[str | None] = mapped_column(String(100), nullable=True)
    list_class: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_default: Mapped[str] = mapped_column(String(1), default="N", server_default="N")
    status: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
