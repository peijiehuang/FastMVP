from datetime import datetime

from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, AuditMixin
from app.models.associations import sys_user_role, sys_user_post


class SysUser(Base, AuditMixin):
    __tablename__ = "sys_user"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    dept_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("sys_dept.dept_id"), nullable=True)
    user_name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    nick_name: Mapped[str] = mapped_column(String(30), nullable=False)
    user_type: Mapped[str] = mapped_column(String(2), default="00", server_default="00")
    email: Mapped[str] = mapped_column(String(50), default="", server_default="")
    phonenumber: Mapped[str] = mapped_column(String(11), default="", server_default="")
    sex: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
    avatar: Mapped[str] = mapped_column(String(100), default="", server_default="")
    password: Mapped[str] = mapped_column(String(100), default="", server_default="")
    status: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
    del_flag: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
    login_ip: Mapped[str] = mapped_column(String(128), default="", server_default="")
    login_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    dept: Mapped["SysDept | None"] = relationship(
        "SysDept", back_populates="users", lazy="joined",
    )
    roles: Mapped[list["SysRole"]] = relationship(
        "SysRole", secondary=sys_user_role, lazy="selectin",
    )
    posts: Mapped[list["SysPost"]] = relationship(
        "SysPost", secondary=sys_user_post, lazy="selectin",
    )
