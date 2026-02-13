from datetime import datetime

from sqlalchemy import BigInteger, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SysLogininfor(Base):
    __tablename__ = "sys_logininfor"

    info_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String(50), default="", server_default="")
    ipaddr: Mapped[str] = mapped_column(String(128), default="", server_default="")
    login_location: Mapped[str] = mapped_column(String(255), default="", server_default="")
    browser: Mapped[str] = mapped_column(String(50), default="", server_default="")
    os: Mapped[str] = mapped_column(String(50), default="", server_default="")
    status: Mapped[str] = mapped_column(String(1), default="0", server_default="0")
    msg: Mapped[str] = mapped_column(String(255), default="", server_default="")
    login_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
