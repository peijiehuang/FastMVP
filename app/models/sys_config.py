from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, AuditMixin


class SysConfig(Base, AuditMixin):
    __tablename__ = "sys_config"

    config_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    config_name: Mapped[str] = mapped_column(String(100), default="", server_default="")
    config_key: Mapped[str] = mapped_column(String(100), default="", server_default="")
    config_value: Mapped[str] = mapped_column(String(500), default="", server_default="")
    config_type: Mapped[str] = mapped_column(String(1), default="N", server_default="N")
