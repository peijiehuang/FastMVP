# RuoYi-FastAPI

基于 Python FastAPI 框架重新实现的 [若依(RuoYi-Vue)](https://gitee.com/y_project/RuoYi-Vue) 后台管理系统后端。除代码生成模块外，与若依官方 Vue2 前端完全兼容，无需修改前端代码即可对接使用。

> **前端适配说明：** 代码生成模块需要对前端做少量修改，因为本项目生成 Python 代码而非原版的 Java 代码。具体改动见下方 [前端修改说明](#前端修改说明) 章节。

## 技术栈

| 类别 | 技术 | 说明 |
|------|------|------|
| Web 框架 | FastAPI + Uvicorn | 高性能 ASGI 异步 Web 框架 |
| ORM | SQLAlchemy 2.x (AsyncIO) + aiomysql | 全异步数据库操作 |
| 数据库 | MySQL | 关系型数据库 |
| 缓存 | Redis | 会话管理、验证码、字典缓存、在线用户 |
| 数据校验 | Pydantic V2 + pydantic-settings | 支持 camelCase 别名，与前端字段无缝对接 |
| 认证 | python-jose (JWT) + passlib (bcrypt) | 无状态令牌认证 + Redis 会话存储 |
| 数据库迁移 | Alembic | 数据库版本管理 |
| 代码生成 | Jinja2 | 模板引擎驱动代码生成 |
| 其他 | openpyxl / Pillow / psutil / httpx | Excel 导出、验证码图片、服务器监控、HTTP 客户端 |

## 功能模块

- **认证管理** -- 登录/登出、图形验证码、用户信息、前端路由菜单
- **用户管理** -- 用户增删改查、个人中心、角色分配、导入导出
- **角色管理** -- 角色增删改查、菜单权限分配、数据权限设置、用户分配
- **菜单管理** -- 菜单增删改查、菜单树
- **部门管理** -- 部门增删改查、部门树
- **岗位管理** -- 岗位增删改查
- **字典管理** -- 字典类型/字典数据维护、Redis 缓存刷新
- **参数配置** -- 系统参数增删改查、Redis 缓存刷新
- **通知公告** -- 通知公告增删改查
- **操作日志** -- 操作日志查询、导出、清空
- **登录日志** -- 登录日志查询、导出、清空、账户解锁
- **在线用户** -- 在线用户查询、强退
- **服务监控** -- 服务器 CPU/内存/磁盘信息
- **缓存监控** -- Redis 缓存信息、键值管理
- **代码生成** -- 数据库表导入、代码预览、生成下载、同步表结构
- **通用接口** -- 文件上传

## 已测试页面

以下页面已通过完整的 CRUD 功能测试（含新增、编辑、删除、查询等操作）：

| 模块 | 页面 | 状态 |
|------|------|------|
| 系统管理 | 用户管理 | 通过 |
| 系统管理 | 角色管理 | 通过 |
| 系统管理 | 岗位管理 | 通过 |
| 系统管理 | 字典管理 | 通过 |
| 系统管理 | 参数设置 | 通过 |
| 系统管理 | 通知公告 | 通过 |
| 系统监控 | 操作日志 | 通过 |
| 系统监控 | 登录日志 | 通过 |
| 系统监控 | 在线用户 | 通过 |
| 系统监控 | 服务监控 | 通过 |
| 系统监控 | 缓存监控 | 通过 |
| 系统工具 | 表单构建 | 通过 |
| 系统工具 | 代码生成 | 通过 |

## 开发过程中修复的问题

| # | 问题描述 | 修复文件 | 根因 |
|---|----------|----------|------|
| 1 | 前端字段 camelCase 与后端 snake_case 不匹配 | `schemas/` | Pydantic 模型未配置驼峰别名 |
| 3 | 缓存监控数据未嵌套在 `data` 字段内 | `api/monitor/cache.py` | `AjaxResult.success(**kwargs)` 将数据放在顶层而非 `data` 内 |
| 4 | 缓存键名格式与前端解析不匹配 | `api/monitor/cache.py` | 缓存名称列表缺少 `cacheName` 字段 |
| 5 | 代码预览 highlight.js 报 "Unknown language" | `services/codegen_service.py` | 预览键格式不符合前端 `vm/lang/name.lang.vm` 解析规则 |
| 6 | 编辑代码生成表时字段信息为空 | `api/tool/gen.py` | 同 #3，响应数据未嵌套在 `data` 字段内 |
| 7 | 生成代码请求被 `/{table_id}` 路由捕获 | `api/tool/gen.py` | 缺少 `/batchGenCode`、`/synchDb` 等端点，且路由顺序不当 |
| 8 | Token 过期后白屏，无法跳转登录页 | `core/exception_handlers.py`, `api/auth/login.py` | AuthException 返回 HTTP 401 而非 HTTP 200 + `code:401`；`/logout` 端点要求有效 token 导致登出死循环 |

## 项目结构

```
FastMVP/
├── app/
│   ├── main.py                # 应用入口，FastAPI 实例与生命周期管理
│   ├── config.py              # 配置管理 (pydantic-settings，读取 .env)
│   ├── api/                   # 路由层 (API Endpoints)
│   │   ├── router.py          # 统一路由注册
│   │   ├── auth/              # 认证路由 (login, logout, info)
│   │   ├── system/            # 系统管理 (user, role, menu, dept, post, dict, config, notice)
│   │   ├── monitor/           # 系统监控 (operlog, logininfor, online, server, cache)
│   │   ├── tool/              # 系统工具 (gen 代码生成)
│   │   └── common.py          # 通用接口 (文件上传)
│   ├── models/                # SQLAlchemy ORM 模型
│   │   ├── base.py            # 声明基类 + AuditMixin 审计字段
│   │   ├── associations.py    # 多对多关联表
│   │   ├── sys_*.py           # 各业务表模型
│   │   └── gen_table.py       # 代码生成表模型
│   ├── schemas/               # Pydantic 请求/响应数据模型 (CamelModel 基类支持驼峰别名)
│   ├── crud/                  # 数据访问层 (CRUDBase 泛型基类 + 各业务 CRUD)
│   ├── services/              # 业务逻辑层 (auth_service, menu_service, codegen_service)
│   ├── core/                  # 核心模块
│   │   ├── security.py        # JWT 令牌 + bcrypt 密码加密
│   │   ├── deps.py            # FastAPI 依赖注入 (当前用户、权限校验)
│   │   ├── data_scope.py      # 数据权限过滤
│   │   ├── decorators.py      # 操作日志装饰器
│   │   ├── redis.py           # Redis 连接管理
│   │   ├── middleware.py      # CORS 等中间件
│   │   ├── response.py        # 统一响应格式
│   │   ├── exceptions.py      # 自定义异常
│   │   ├── exception_handlers.py  # 全局异常处理
│   │   └── constants.py       # 系统常量
│   ├── db/
│   │   └── session.py         # 异步数据库会话工厂
│   └── utils/                 # 工具类 (captcha, excel_utils, ip_utils)
├── sql/
│   └── init_data.sql          # 数据库初始化脚本 (表结构 + 基础数据)
├── templates/                 # 代码生成 Jinja2 模板 (model, schema, crud, api)
├── alembic/                   # Alembic 数据库迁移
├── alembic.ini                # Alembic 配置
├── .env.example               # 环境变量示例
├── requirements.txt           # Python 依赖清单
└── pyproject.toml             # 项目元数据
```

## 快速开始

### 环境要求

- Python >= 3.10
- MySQL >= 5.7
- Redis >= 5.0

### 1. 克隆项目

```bash
git clone <仓库地址>
cd FastMVP
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 3. 初始化数据库

在 MySQL 中创建数据库并导入初始化数据：

```sql
CREATE DATABASE ruoyi_fast DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

```bash
mysql -u root -p ruoyi_fast < sql/init_data.sql
```

### 4. 配置环境变量

复制示例配置文件并根据实际环境修改：

```bash
cp .env.example .env
```

主要配置项：

```ini
# 数据库连接 (修改用户名、密码、数据库名)
DATABASE_URL=mysql+aiomysql://root:your_password@localhost:3306/ruoyi_fast

# Redis 连接
REDIS_URL=redis://localhost:6379/0

# JWT 密钥 (生产环境务必修改为随机字符串)
JWT_SECRET=your-secret-key-change-in-production

# Token 过期时间 (分钟)
TOKEN_EXPIRE_MINUTES=30
```

### 5. 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

启动成功后可访问：

| 地址 | 说明 |
|------|------|
| http://localhost:8080/docs | Swagger UI 交互式 API 文档 |
| http://localhost:8080/redoc | ReDoc 风格 API 文档 |
| http://localhost:8080/health | 健康检查接口 |

### 6. 前端对接

使用若依官方 Vue2 前端 [RuoYi-Vue](https://gitee.com/y_project/RuoYi-Vue)，将前端代理地址指向 `http://localhost:8080` 即可。

## 默认账户

| 账号 | 密码 |
|------|------|
| admin | admin123 |

## 前端修改说明

由于本项目生成 Python 代码而非 Java 代码，需要对若依官方前端 `ruoyi-ui` 做以下少量修改：

**文件：** `src/views/tool/gen/index.vue`

1. **注册 Python 语法高亮**：添加 highlight.js 的 Python 语言支持

   ```javascript
   hljs.registerLanguage("python", require("highlight.js/lib/languages/python"))
   ```

2. **修改预览默认 Tab**：将预览弹窗的默认激活标签从 Java 改为 Python

   ```javascript
   // 修改前
   activeName: "domain.java"

   // 修改后
   activeName: "model.python"
   ```

   共两处：`data()` 中的初始值和 `handlePreview()` 方法中的赋值。

## License

MIT
