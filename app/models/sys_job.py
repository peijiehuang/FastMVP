from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, AuditMixin


class SysJob(Base, AuditMixin):
    __tablename__ = "sys_job"

    job_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_name: Mapped[str] = mapped_column(String(64), default="")
    job_group: Mapped[str] = mapped_column(String(64), default="DEFAULT")
    invoke_target: Mapped[str] = mapped_column(String(500), default="")
    cron_expression: Mapped[str] = mapped_column(String(255), default="")
    misfire_policy: Mapped[str] = mapped_column(String(20), default="3")
    concurrent: Mapped[str] = mapped_column(String(1), default="1")
    status: Mapped[str] = mapped_column(String(1), default="0")
