<p align="center">
  <h1 align="center">RuoYi-FastAPI</h1>
  <p align="center">
    基于 FastAPI 全异步重构的若依后台管理系统 API
    <br />
    <em>高性能 · 现代化 · 开箱即用</em>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0+-red?logo=python&logoColor=white" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/MySQL-8.0+-4479A1?logo=mysql&logoColor=white" alt="MySQL">
  <img src="https://img.shields.io/badge/Redis-5.0+-DC382D?logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

---

## 📖 项目简介

**RuoYi-FastAPI** 是 [RuoYi-Vue](https://gitee.com/y_project/RuoYi-Vue) 后端的 **Python 全异步重构版本**，使用 FastAPI 框架替代原有的 Spring Boot，保持与 RuoYi-Vue 前端的 **100% API 兼容**。

### 为什么选择这个项目？

| 对比维度 | Spring Boot (原版) | FastAPI (本项目) |
|---------|-------------------|-----------------|
| 启动速度 | ~10s | **< 1s** |
| 内存占用 | ~300MB+ | **< 50MB** |
| 开发效率 | Java 冗长模板代码 | **Python 简洁表达** |
| 异步支持 | WebFlux (复杂) | **原生 async/await** |
| API 文档 | Swagger 手动配置 | **自动生成 OpenAPI** |
| 部署难度 | JDK + Maven | **pip install** |

> [!NOTE]
> 本项目与 RuoYi-Vue 前端完全兼容，无需修改前端代码即可直接对接使用。

---

## 🏗️ 技术栈

| 类别 | 技术 | 说明 |
|------|------|------|
| **Web 框架** | FastAPI 0.115+ | 高性能异步 Web 框架 |
| **ORM** | SQLAlchemy 2.0+ (AsyncIO) | 全异步数据库操作 |
| **数据库驱动** | aiomysql | MySQL 异步驱动 |
| **缓存** | Redis 5.0+ (aioredis) | 会话管理 / 字典缓存 / 验证码 |
| **认证** | python-jose + passlib | JWT Token + Bcrypt 密码加密 |
| **数据校验** | Pydantic 2.7+ | 请求/响应数据模型验证 |
| **配置管理** | pydantic-settings | .env 环境变量管理 |
| **数据库迁移** | Alembic | 安全的数据库版本管理 |
| **Excel** | openpyxl | 数据导入/导出 |
| **验证码** | Pillow | 图形验证码生成 |
| **模板引擎** | Jinja2 | 代码生成模板 |
| **HTTP 客户端** | httpx | 异步 HTTP 请求 |
| **系统监控** | psutil | 服务器 CPU/内存/磁盘监控 |

---

## ✨ 功能模块

### ✅ 系统管理

| 模块 | 路由前缀 | 功能说明 |
|------|---------|---------|
| 用户管理 | `/system/user` | 用户 CRUD、头像上传、密码重置、角色分配、导入导出 |
| 角色管理 | `/system/role` | 角色 CRUD、菜单权限分配、数据权限设置、用户分配 |
| 菜单管理 | `/system/menu` | 菜单 CRUD、菜单树、角色菜单树 |
| 部门管理 | `/system/dept` | 部门 CRUD、部门树、层级管理 |
| 岗位管理 | `/system/post` | 岗位 CRUD、导出 |
| 字典管理 | `/system/dict/type` `/system/dict/data` | 字典类型和字典数据管理、Redis 缓存 |
| 参数配置 | `/system/config` | 系统参数 CRUD、Redis 缓存、导出 |
| 通知公告 | `/system/notice` | 通知公告 CRUD |

### ✅ 系统监控

| 模块 | 路由前缀 | 功能说明 |
|------|---------|---------|
| 操作日志 | `/monitor/operlog` | 操作日志查询、导出、清空 |
| 登录日志 | `/monitor/logininfor` | 登录日志查询、导出、清空、账户解锁 |
| 在线用户 | `/monitor/online` | 在线用户查询、强退 |
| 服务监控 | `/monitor/server` | 服务器 CPU / 内存 / JVM / 磁盘实时监控 |
| 缓存监控 | `/monitor/cache` | Redis 信息查看、缓存键管理（查看/删除/清空）|

### ✅ 认证中心

| 功能 | 端点 | 说明 |
|------|------|------|
| 用户登录 | `POST /login` | 用户名密码 + 验证码登录 |
| 用户登出 | `POST /logout` | 清除 Redis 会话 |
| 获取验证码 | `GET /captchaImage` | 生成图形验证码 |
| 获取用户信息 | `GET /getInfo` | 用户信息 + 权限 + 角色 |
| 获取路由菜单 | `GET /getRouters` | 前端动态路由菜单 |

### 🚧 代码生成 (开发中)

| 模块 | 路由前缀 | 功能说明 |
|------|---------|---------|
| 代码生成 | `/tool/gen` | 数据库表导入、代码预览、生成下载 |

> [!WARNING]
> 代码生成模块的基础框架已完成（表导入、元数据管理、Jinja2 模板预览），但**代码下载与批量生成功能仍在开发中**，暂不建议在生产环境使用此模块。

### ✅ 通用接口

| 功能 | 端点 | 说明 |
|------|------|------|
| 文件上传 | `POST /common/upload` | 通用文件上传 |
| 健康检查 | `GET /health` | 服务健康状态 |

---

## 🏛️ 架构设计

```
请求 → FastAPI Router → 依赖注入 (认证/权限) → Service → CRUD → SQLAlchemy → MySQL
                            ↕                                          ↕
                          Redis                                     Alembic
                    (会话/缓存/验证码)                              (数据库迁移)
```

### 分层架构

| 层级 | 目录 | 职责 |
|------|------|------|
| **路由层** | `app/api/` | 接收请求、参数校验、权限检查、调用 Service |
| **服务层** | `app/services/` | 业务逻辑、事务编排 |
| **数据层** | `app/crud/` | 数据库 CRUD 操作，通用 `CRUDBase` 泛型基类 |
| **模型层** | `app/models/` | SQLAlchemy ORM 模型定义 |
| **数据校验** | `app/schemas/` | Pydantic 请求/响应数据模型 |
| **核心层** | `app/core/` | 认证、权限、中间件、异常处理、Redis |
| **工具层** | `app/utils/` | 验证码、Excel、IP 解析等工具 |

### 核心设计特性

- **全异步架构**：从 Web 框架到数据库驱动全链路 async/await
- **RBAC 权限控制**：基于 `has_permi()` / `has_role()` 的声明式权限依赖注入
- **五级数据权限**：全部数据 / 自定义 / 本部门 / 本部门及子部门 / 仅本人
- **Redis 会话管理**：JWT Token 无状态认证 + Redis 存储用户信息 / 自动续期
- **通用 CRUD 泛型基类**：`CRUDBase[Model, CreateSchema, UpdateSchema]` 自动分页
- **操作日志装饰器**：`@log_operation(title, business_type)` 自动记录操作日志
- **统一响应格式**：`AjaxResult` / `TableDataInfo` 与 RuoYi 前端完全兼容
- **全局异常处理**：`ServiceException` / `AuthException` / `ForbiddenException` 分层处理

---

## 🚀 快速开始

### 环境要求

| 依赖 | 版本要求 |
|------|---------|
| Python | ≥ 3.10 |
| MySQL | ≥ 8.0 |
| Redis | ≥ 5.0 |

### 1. 克隆项目

```bash
git clone https://github.com/peijiehuang/FastMVP.git
cd FastMVP
```

### 2. 创建虚拟环境

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，修改以下配置：

```ini
# 数据库连接（修改用户名、密码、数据库名）
DATABASE_URL=mysql+aiomysql://root:your_password@localhost:3306/ruoyi_fast

# Redis 连接
REDIS_URL=redis://localhost:6379/0

# JWT 密钥（生产环境请修改为随机字符串）
JWT_SECRET=your-secret-key-change-in-production
```

### 5. 初始化数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE ruoyi_fast DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"

# 导入初始数据
mysql -u root -p ruoyi_fast < sql/init_data.sql
```

### 6. 启动服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# 或使用 FastAPI CLI
fastapi dev app/main.py --port 8080
```

### 7. 访问服务

| 地址 | 说明 |
|------|------|
| http://localhost:8080/docs | Swagger UI 交互式 API 文档 |
| http://localhost:8080/redoc | ReDoc 风格 API 文档 |
| http://localhost:8080/health | 健康检查 |

> [!TIP]
> 默认管理员账号：`admin` / `admin123`

---

## 📁 项目目录结构

```
FastMVP/
├── app/                          # 应用主目录
│   ├── main.py                   # FastAPI 应用入口、生命周期管理
│   ├── config.py                 # Pydantic Settings 配置管理
│   ├── api/                      # 路由层 (API Endpoints)
│   │   ├── router.py             # 路由注册中心
│   │   ├── auth/                 # 认证相关路由
│   │   │   ├── login.py          # 登录 / 登出 / 验证码
│   │   │   └── info.py           # 用户信息 / 路由菜单
│   │   ├── system/               # 系统管理路由
│   │   │   ├── user.py           # 用户管理
│   │   │   ├── role.py           # 角色管理
│   │   │   ├── menu.py           # 菜单管理
│   │   │   ├── dept.py           # 部门管理
│   │   │   ├── post.py           # 岗位管理
│   │   │   ├── dict_type.py      # 字典类型
│   │   │   ├── dict_data.py      # 字典数据
│   │   │   ├── config.py         # 参数配置
│   │   │   └── notice.py         # 通知公告
│   │   ├── monitor/              # 系统监控路由
│   │   │   ├── operlog.py        # 操作日志
│   │   │   ├── logininfor.py     # 登录日志
│   │   │   ├── online.py         # 在线用户
│   │   │   ├── server.py         # 服务监控
│   │   │   └── cache.py          # 缓存监控
│   │   ├── tool/                 # 系统工具路由
│   │   │   └── gen.py            # 代码生成 (🚧 开发中)
│   │   └── common.py             # 通用接口 (文件上传)
│   ├── services/                 # 服务层 (业务逻辑)
│   │   ├── auth_service.py       # 认证服务 (登录/登出/权限)
│   │   ├── codegen_service.py    # 代码生成服务 (🚧 开发中)
│   │   └── menu_service.py       # 菜单服务 (路由树构建)
│   ├── crud/                     # 数据访问层 (CRUD)
│   │   ├── base.py               # CRUDBase 泛型基类
│   │   ├── crud_user.py          # 用户 CRUD
│   │   ├── crud_role.py          # 角色 CRUD
│   │   ├── crud_menu.py          # 菜单 CRUD
│   │   ├── crud_dept.py          # 部门 CRUD
│   │   ├── crud_post.py          # 岗位 CRUD
│   │   ├── crud_dict_type.py     # 字典类型 CRUD
│   │   ├── crud_dict_data.py     # 字典数据 CRUD
│   │   ├── crud_config.py        # 参数配置 CRUD
│   │   ├── crud_notice.py        # 通知公告 CRUD
│   │   ├── crud_oper_log.py      # 操作日志 CRUD
│   │   └── crud_logininfor.py    # 登录日志 CRUD
│   ├── models/                   # 模型层 (ORM 模型)
│   │   ├── base.py               # Base + AuditMixin 审计字段
│   │   ├── associations.py       # 多对多关联表
│   │   ├── sys_user.py           # 用户模型
│   │   ├── sys_role.py           # 角色模型
│   │   ├── sys_menu.py           # 菜单模型
│   │   ├── sys_dept.py           # 部门模型
│   │   ├── sys_post.py           # 岗位模型
│   │   ├── sys_dict_type.py      # 字典类型模型
│   │   ├── sys_dict_data.py      # 字典数据模型
│   │   ├── sys_config.py         # 参数配置模型
│   │   ├── sys_notice.py         # 通知公告模型
│   │   ├── sys_oper_log.py       # 操作日志模型
│   │   ├── sys_logininfor.py     # 登录日志模型
│   │   └── gen_table.py          # 代码生成表模型
│   ├── schemas/                  # 数据校验层 (Pydantic Schema)
│   │   ├── auth.py               # 认证相关 Schema
│   │   ├── sys_user.py           # 用户 Schema
│   │   ├── sys_role.py           # 角色 Schema
│   │   ├── sys_menu.py           # 菜单 Schema
│   │   ├── sys_dept.py           # 部门 Schema
│   │   ├── sys_post.py           # 岗位 Schema
│   │   ├── sys_dict.py           # 字典 Schema
│   │   ├── sys_config.py         # 参数配置 Schema
│   │   └── sys_notice.py         # 通知公告 Schema
│   ├── core/                     # 核心层 (框架基础设施)
│   │   ├── security.py           # JWT + Bcrypt 安全工具
│   │   ├── deps.py               # 依赖注入 (认证/权限)
│   │   ├── data_scope.py         # 数据权限过滤器
│   │   ├── decorators.py         # 操作日志装饰器
│   │   ├── constants.py          # 系统常量定义
│   │   ├── response.py           # 统一响应模型
│   │   ├── exceptions.py         # 自定义异常类
│   │   ├── exception_handlers.py # 全局异常处理器
│   │   ├── middleware.py         # 中间件配置
│   │   └── redis.py              # Redis 连接管理
│   ├── db/                       # 数据库层
│   │   └── session.py            # 异步 Session 工厂
│   └── utils/                    # 工具层
│       ├── captcha.py            # 验证码生成
│       ├── excel_utils.py        # Excel 导入导出
│       └── ip_utils.py           # IP 地址解析
├── alembic/                      # 数据库迁移脚本
├── sql/
│   └── init_data.sql             # 初始化数据脚本
├── templates/                    # 代码生成 Jinja2 模板
│   ├── api.py.j2                 # API 路由模板
│   ├── crud.py.j2                # CRUD 模板
│   ├── model.py.j2               # ORM 模型模板
│   └── schema.py.j2              # Pydantic Schema 模板
├── uploads/                      # 文件上传目录
├── pyproject.toml                # 项目元数据
├── requirements.txt              # 依赖清单
├── .env.example                  # 环境变量模板
├── alembic.ini                   # Alembic 迁移配置
└── test_all_api.py               # API 集成测试
```

---

## 🔧 开发指南

### 添加新模块

以"公告管理"为例，添加一个新模块需要以下步骤：

#### 1. 定义 ORM 模型 (`app/models/`)

```python
# app/models/sys_notice.py
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, AuditMixin

class SysNotice(Base, AuditMixin):
    __tablename__ = "sys_notice"
    notice_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    notice_title: Mapped[str] = mapped_column(String(50))
    notice_type: Mapped[str] = mapped_column(String(1))
    notice_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(1), default="0")
```

#### 2. 定义数据校验 (`app/schemas/`)

```python
# app/schemas/sys_notice.py
from pydantic import BaseModel

class NoticeCreate(BaseModel):
    notice_title: str
    notice_type: str
    notice_content: str | None = None
    status: str = "0"
```

#### 3. 实现 CRUD 操作 (`app/crud/`)

```python
# app/crud/crud_notice.py
from app.crud.base import CRUDBase
from app.models.sys_notice import SysNotice
from app.schemas.sys_notice import NoticeCreate

class CRUDNotice(CRUDBase[SysNotice, NoticeCreate, dict]):
    pass

notice = CRUDNotice(SysNotice)
```

#### 4. 编写 API 路由 (`app/api/system/`)

```python
# app/api/system/notice.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import has_permi
from app.core.decorators import log_operation
from app.crud.crud_notice import notice as notice_crud
from app.db.session import get_db

router = APIRouter()

@router.get("/list")
async def list_notices(
    current_user: dict = Depends(has_permi("system:notice:list")),
    db: AsyncSession = Depends(get_db),
):
    items, total = await notice_crud.get_list(db)
    return {"code": 200, "rows": [...], "total": total}
```

#### 5. 注册路由 (`app/api/router.py`)

```python
from app.api.system import notice
api_router.include_router(notice.router, prefix="/system/notice", tags=["通知公告"])
```

### 权限控制

```python
# 权限字符串检查
@router.get("/list")
async def list_users(current_user = Depends(has_permi("system:user:list"))):
    ...

# 角色检查
@router.delete("/{user_id}")
async def delete_user(current_user = Depends(has_role("admin"))):
    ...
```

### 操作日志

```python
from app.core.decorators import log_operation
from app.core.constants import BusinessType

@router.post("")
@log_operation(title="用户管理", business_type=BusinessType.INSERT)
async def create_user(request: Request, current_user = Depends(has_permi("system:user:add"))):
    ...
```

### 数据权限

```python
from app.core.data_scope import apply_data_scope

# 在查询中应用数据权限过滤
query = select(SysUser).join(SysDept)
query = apply_data_scope(query, current_user)
```

---

## 📋 API 文档

启动服务后访问以下地址查看完整 API 文档：

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

### API 分组概览

| 分组 | 包含接口 |
|------|---------|
| 认证管理 | 登录、登出、验证码、用户信息、路由菜单 |
| 通用接口 | 文件上传 |
| 用户管理 | 用户 CRUD、个人中心、分配角色 |
| 角色管理 | 角色 CRUD、数据权限、分配用户 |
| 菜单管理 | 菜单 CRUD、菜单树 |
| 部门管理 | 部门 CRUD、部门树 |
| 岗位管理 | 岗位 CRUD |
| 字典类型 | 字典类型 CRUD、缓存刷新 |
| 字典数据 | 字典数据 CRUD |
| 参数配置 | 系统参数 CRUD、缓存刷新 |
| 通知公告 | 通知公告 CRUD |
| 操作日志 | 操作日志查询、导出、清空 |
| 登录日志 | 登录日志查询、导出、清空、解锁 |
| 在线用户 | 在线用户查询、强退 |
| 服务监控 | CPU / 内存 / 磁盘监控 |
| 缓存监控 | Redis 信息、键值管理 |
| 代码生成 | 表导入、代码预览、生成下载 🚧 |

---

## 🧪 测试

项目包含完整的 API 集成测试：

```bash
# 运行全部测试
python -m pytest test_all_api.py -v

# 运行指定测试
python -m pytest test_all_api.py::TestAuthAPI -v
```

---

## 🔄 数据库迁移

使用 Alembic 管理数据库 Schema 变更：

```bash
# 生成迁移脚本
alembic revision --autogenerate -m "描述变更内容"

# 执行迁移
alembic upgrade head

# 回退一个版本
alembic downgrade -1

# 查看迁移历史
alembic history
```

---

## 🗺️ 路线图

- [x] 认证中心（登录 / 登出 / 验证码）
- [x] 用户管理（CRUD / 导入导出 / 角色分配）
- [x] 角色管理（CRUD / 菜单权限 / 数据权限）
- [x] 菜单管理（CRUD / 菜单树）
- [x] 部门管理（CRUD / 部门树）
- [x] 岗位管理（CRUD / 导出）
- [x] 字典管理（类型 + 数据 / Redis 缓存）
- [x] 参数配置（CRUD / Redis 缓存）
- [x] 通知公告
- [x] 操作日志 / 登录日志
- [x] 在线用户管理
- [x] 服务器监控（CPU / 内存 / 磁盘）
- [x] 缓存监控（Redis 信息 / 键值管理）
- [x] 数据权限（五级数据权限过滤）
- [ ] 代码生成（表导入 ✅ / 预览 ✅ / 下载 🚧）
- [ ] 定时任务管理
- [ ] 国际化支持
- [ ] Docker 部署方案

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

<p align="center">
  <strong>⭐ 如果这个项目对你有帮助，请给一个 Star 吧！</strong>
</p>
