from sqlalchemy import BigInteger, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, AuditMixin


class SysMenu(Base, AuditMixin):
    __tablename__ = "sys_menu"

    menu_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    menu_name: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_id: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    order_num: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    path: Mapped[str] = mapped_column(String(200), default="", server_default="")
    component: Mapped[str | None] = mapped_column(String(255), nullable=True)
    query: Mapped[str | None] = mapped_column(String(255), nullable=True)
    route_name: Mapped[str] = mapped_column(String(50), default="", server_default="")
    is_frame: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    is_cache: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    menu_type: Mapped[str] = mapped_column(String(1), default="", server_default="")
    visible: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
    status: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
    perms: Mapped[str | None] = mapped_column(String(100), nullable=True)
    icon: Mapped[str] = mapped_column(String(100), default="#", server_default="#")
