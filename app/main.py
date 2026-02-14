import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.middleware import setup_middleware
from app.core.redis import close_redis, init_redis
from app.services.job_service import init_scheduler, shutdown_scheduler
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    await init_redis()
    await init_scheduler(app)
    yield
    # Shutdown
    await shutdown_scheduler()
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="基于 FastAPI 实现的若依(RuoYi)后台管理系统 API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "认证管理", "description": "登录、登出、验证码、用户信息、路由菜单"},
        {"name": "通用接口", "description": "文件上传等通用功能"},
        {"name": "用户管理", "description": "用户的增删改查、个人中心、分配角色"},
        {"name": "角色管理", "description": "角色的增删改查、数据权限、分配用户"},
        {"name": "菜单管理", "description": "菜单的增删改查、菜单树"},
        {"name": "部门管理", "description": "部门的增删改查、部门树"},
        {"name": "岗位管理", "description": "岗位的增删改查"},
        {"name": "字典类型", "description": "字典类型的增删改查、缓存刷新"},
        {"name": "字典数据", "description": "字典数据的增删改查"},
        {"name": "参数配置", "description": "系统参数的增删改查、缓存刷新"},
        {"name": "通知公告", "description": "通知公告的增删改查"},
        {"name": "操作日志", "description": "操作日志查询、导出、清空"},
        {"name": "登录日志", "description": "登录日志查询、导出、清空、解锁"},
        {"name": "在线用户", "description": "在线用户查询、强退"},
        {"name": "服务监控", "description": "服务器 CPU/内存/磁盘监控"},
        {"name": "缓存监控", "description": "Redis 缓存信息、键值管理"},
        {"name": "定时任务", "description": "定时任务的增删改查、状态切换、立即执行"},
        {"name": "调度日志", "description": "调度日志查询、删除、清空"},
        {"name": "数据监控", "description": "数据库连接池监控"},
        {"name": "代码生成", "description": "数据库表导入、代码预览、生成下载"},
    ],
)

# Setup middleware
setup_middleware(app)

# Register exception handlers
register_exception_handlers(app)

# Include API routers
app.include_router(api_router)

# Static files for uploads (avatar, files)
upload_path = os.path.abspath(settings.UPLOAD_PATH)
os.makedirs(upload_path, exist_ok=True)
app.mount("/profile", StaticFiles(directory=upload_path), name="uploads")


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}

