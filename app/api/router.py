from fastapi import APIRouter

from app.api.auth import login, info
from app.api.common import router as common_router
from app.api.system import user, role, menu, dept, post, dict_type, dict_data, config, notice
from app.api.monitor import operlog, logininfor, online, server, cache, job, job_log, druid
from app.api.tool import gen

api_router = APIRouter()

# Auth routes (root level, no prefix)
api_router.include_router(login.router, tags=["认证管理"])
api_router.include_router(info.router, tags=["认证管理"])

# Common routes
api_router.include_router(common_router, tags=["通用接口"])

# System Management routes
api_router.include_router(user.router, prefix="/system/user", tags=["用户管理"])
api_router.include_router(role.router, prefix="/system/role", tags=["角色管理"])
api_router.include_router(menu.router, prefix="/system/menu", tags=["菜单管理"])
api_router.include_router(dept.router, prefix="/system/dept", tags=["部门管理"])
api_router.include_router(post.router, prefix="/system/post", tags=["岗位管理"])
api_router.include_router(dict_type.router, prefix="/system/dict/type", tags=["字典类型"])
api_router.include_router(dict_data.router, prefix="/system/dict/data", tags=["字典数据"])
api_router.include_router(config.router, prefix="/system/config", tags=["参数配置"])
api_router.include_router(notice.router, prefix="/system/notice", tags=["通知公告"])

# System Monitor routes
api_router.include_router(operlog.router, prefix="/monitor/operlog", tags=["操作日志"])
api_router.include_router(logininfor.router, prefix="/monitor/logininfor", tags=["登录日志"])
api_router.include_router(online.router, prefix="/monitor/online", tags=["在线用户"])
api_router.include_router(server.router, prefix="/monitor/server", tags=["服务监控"])
api_router.include_router(cache.router, prefix="/monitor/cache", tags=["缓存监控"])
api_router.include_router(job.router, prefix="/monitor/job", tags=["定时任务"])
api_router.include_router(job_log.router, prefix="/monitor/jobLog", tags=["调度日志"])
api_router.include_router(druid.router, prefix="/druid", tags=["数据监控"])

# System Tools routes
api_router.include_router(gen.router, prefix="/tool/gen", tags=["代码生成"])
