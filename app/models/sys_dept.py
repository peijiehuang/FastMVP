from datetime import datetime

from sqlalchemy import BigInteger, String, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, AuditMixin


class SysDept(Base, AuditMixin):
    __tablename__ = "sys_dept"

    dept_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    ancestors: Mapped[str] = mapped_column(String(50), default="", server_default="")
    dept_name: Mapped[str] = mapped_column(String(30), default="", server_default="")
    order_num: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    leader: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(11), nullable=True)
    email: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
    del_flag: Mapped[str] = mapped_column(String(1), default="0", server_default="0")

    # Relationships
    users: Mapped[list["SysUser"]] = relationship(back_populates="dept", lazy="noload")
