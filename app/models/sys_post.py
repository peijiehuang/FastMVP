from sqlalchemy import BigInteger, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, AuditMixin


class SysPost(Base, AuditMixin):
    __tablename__ = "sys_post"

    post_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    post_code: Mapped[str] = mapped_column(String(64), nullable=False)
    post_name: Mapped[str] = mapped_column(String(50), nullable=False)
    post_sort: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(1), nullable=False, default="0", server_default="0")
