from sqlalchemy import BigInteger, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, AuditMixin


class SysDictType(Base, AuditMixin):
    __tablename__ = "sys_dict_type"

    dict_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    dict_name: Mapped[str] = mapped_column(String(100), default="", server_default="")
    dict_type: Mapped[str] = mapped_column(String(100), unique=True, default="", server_default="")
    status: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
