from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, AuditMixin


class SysNotice(Base, AuditMixin):
    __tablename__ = "sys_notice"

    notice_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    notice_title: Mapped[str] = mapped_column(String(50), nullable=False)
    notice_type: Mapped[str] = mapped_column(String(1), nullable=False)
    notice_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
