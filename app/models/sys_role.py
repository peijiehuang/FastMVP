from sqlalchemy import BigInteger, String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, AuditMixin
from app.models.associations import sys_role_menu, sys_role_dept


class SysRole(Base, AuditMixin):
    __tablename__ = "sys_role"

    role_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role_name: Mapped[str] = mapped_column(String(30), nullable=False)
    role_key: Mapped[str] = mapped_column(String(100), nullable=False)
    role_sort: Mapped[int] = mapped_column(Integer, nullable=False)
    data_scope: Mapped[str] = mapped_column(String(1), default="1", server_default="1")
    menu_check_strictly: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    dept_check_strictly: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    status: Mapped[str] = mapped_column(String(1), nullable=False, default="0", server_default="0")
    del_flag: Mapped[str] = mapped_column(String(1), default="0", server_default="0")

    # Relationships
    menus: Mapped[list["SysMenu"]] = relationship(
        "SysMenu", secondary=sys_role_menu, lazy="selectin",
    )
    depts: Mapped[list["SysDept"]] = relationship(
        "SysDept", secondary=sys_role_dept, lazy="selectin",
    )
