import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# this is the Alembic Config object
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models so Alembic can detect them
from app.models.base import Base
from app.models.associations import *  # noqa
from app.models.sys_user import SysUser  # noqa
from app.models.sys_role import SysRole  # noqa
from app.models.sys_menu import SysMenu  # noqa
from app.models.sys_dept import SysDept  # noqa
from app.models.sys_post import SysPost  # noqa
from app.models.sys_dict_type import SysDictType  # noqa
from app.models.sys_dict_data import SysDictData  # noqa
from app.models.sys_config import SysConfig  # noqa
from app.models.sys_notice import SysNotice  # noqa
from app.models.sys_oper_log import SysOperLog  # noqa
from app.models.sys_logininfor import SysLogininfor  # noqa
from app.models.gen_table import GenTable, GenTableColumn  # noqa

from app.config import settings

target_metadata = Base.metadata

# Override sqlalchemy.url with app settings
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL.replace("+aiomysql", "+pymysql"),
)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
