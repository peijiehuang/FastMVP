from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.sys_config import SysConfig
from app.schemas.sys_config import ConfigCreate, ConfigUpdate


class CRUDConfig(CRUDBase[SysConfig, ConfigCreate, ConfigUpdate]):

    async def get_config_list(
        self,
        db: AsyncSession,
        *,
        page_num: int = 1,
        page_size: int = 10,
        config_name: str | None = None,
        config_key: str | None = None,
        config_type: str | None = None,
        begin_time: str | None = None,
        end_time: str | None = None,
    ) -> tuple[Sequence[SysConfig], int]:
        query = select(SysConfig)
        if config_name:
            query = query.where(SysConfig.config_name.like(f"%{config_name}%"))
        if config_key:
            query = query.where(SysConfig.config_key.like(f"%{config_key}%"))
        if config_type:
            query = query.where(SysConfig.config_type == config_type)
        if begin_time:
            query = query.where(SysConfig.create_time >= begin_time)
        if end_time:
            query = query.where(SysConfig.create_time <= end_time)
        query = query.order_by(SysConfig.config_id)
        return await self.get_list(db, query=query, page_num=page_num, page_size=page_size)

    async def get_by_key(self, db: AsyncSession, config_key: str) -> SysConfig | None:
        result = await db.execute(
            select(SysConfig).where(SysConfig.config_key == config_key)
        )
        return result.scalar_one_or_none()

    async def create_config(self, db: AsyncSession, obj_in: ConfigCreate, create_by: str) -> SysConfig:
        cfg = SysConfig(**obj_in.model_dump(), create_by=create_by)
        db.add(cfg)
        await db.flush()
        await db.refresh(cfg)
        return cfg

    async def update_config(self, db: AsyncSession, obj_in: ConfigUpdate, update_by: str) -> SysConfig | None:
        cfg = await self.get(db, obj_in.config_id)
        if not cfg:
            return None
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"config_id"})
        update_data["update_by"] = update_by
        update_data["update_time"] = datetime.now()
        for k, v in update_data.items():
            setattr(cfg, k, v)
        await db.flush()
        return cfg


crud_config = CRUDConfig(SysConfig)
