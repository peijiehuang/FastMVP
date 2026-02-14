from datetime import datetime

from sqlalchemy import BigInteger, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SysJobLog(Base):
    __tablename__ = "sys_job_log"

    job_log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_name: Mapped[str] = mapped_column(String(64), default="")
    job_group: Mapped[str] = mapped_column(String(64), default="")
    invoke_target: Mapped[str] = mapped_column(String(500), default="")
    job_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(1), default="0")
    exception_info: Mapped[str] = mapped_column(String(2000), default="")
    create_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
