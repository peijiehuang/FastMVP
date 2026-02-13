from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""
    pass


class AuditMixin:
    """Mixin providing RuoYi standard audit columns."""

    create_by: Mapped[str] = mapped_column(
        String(64), default="", server_default=""
    )
    create_time: Mapped[datetime | None] = mapped_column(
        DateTime, default=func.now(), server_default=func.now()
    )
    update_by: Mapped[str] = mapped_column(
        String(64), default="", server_default=""
    )
    update_time: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )
    remark: Mapped[str | None] = mapped_column(
        String(500), nullable=True, default=None
    )
