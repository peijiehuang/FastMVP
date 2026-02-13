from datetime import datetime

from sqlalchemy import BigInteger, String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SysOperLog(Base):
    __tablename__ = "sys_oper_log"

    oper_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50), default="", server_default="")
    business_type: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    method: Mapped[str] = mapped_column(String(200), default="", server_default="")
    request_method: Mapped[str] = mapped_column(String(10), default="", server_default="")
    operator_type: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    oper_name: Mapped[str] = mapped_column(String(50), default="", server_default="")
    dept_name: Mapped[str] = mapped_column(String(50), default="", server_default="")
    oper_url: Mapped[str] = mapped_column(String(255), default="", server_default="")
    oper_ip: Mapped[str] = mapped_column(String(128), default="", server_default="")
    oper_location: Mapped[str] = mapped_column(String(255), default="", server_default="")
    oper_param: Mapped[str] = mapped_column(String(2000), default="", server_default="")
    json_result: Mapped[str] = mapped_column(String(2000), default="", server_default="")
    status: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    error_msg: Mapped[str] = mapped_column(String(2000), default="", server_default="")
    oper_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cost_time: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
