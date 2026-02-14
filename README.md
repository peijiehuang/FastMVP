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
| 定时任务 | APScheduler 3.x (AsyncIOScheduler) | Quartz cron 表达式兼容，支持并发控制 |
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
- **定时任务** -- 定时任务增删改查、启停切换、立即执行 (APScheduler)
- **调度日志** -- 调度执行日志查询、删除、清空
- **数据监控** -- SQLAlchemy 连接池状态监控 (替代 Java Druid)
- **代码生成** -- 数据库表导入、代码预览、生成下载、同步表结构
- **通用接口** -- 文件上传

---

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

使用若依官方 Vue2 前端 [RuoYi-Vue](https://gitee.com/y_project/RuoYi-Vue)，将前端 `vue.config.js` 中的代理地址指向本项目：

```javascript
// vue.config.js
devServer: {
  proxy: {
    '/dev-api': {
      target: 'http://localhost:8080',
      changeOrigin: true,
      pathRewrite: { '^/dev-api': '' }
    }
  }
}
```

### 默认账户

| 账号 | 密码 |
|------|------|
| admin | admin123 |

---

## 各模块使用教程

### 认证管理

系统使用 JWT + Redis 实现无状态认证。

- **登录**：访问前端登录页，输入账号密码和验证码。后端验证通过后生成 JWT Token 并存入 Redis，前端将 Token 保存在 Cookie (`Admin-Token`) 中。
- **登出**：点击右上角头像 → 退出登录。后端从 Redis 中删除 Token，前端清除 Cookie 并跳转登录页。
- **验证码**：登录页自动加载图形验证码，点击可刷新。验证码存储在 Redis 中，有效期 2 分钟。
- **Token 续期**：每次请求自动刷新 Token 的 Redis 过期时间，默认 30 分钟无操作后过期。

### 用户管理

路径：系统管理 → 用户管理

- **查询**：左侧部门树点击可按部门筛选，顶部支持按用户名、手机号、状态、创建时间搜索。
- **新增**：点击"新增"按钮，填写用户名、昵称、密码、部门、岗位、角色等信息。
- **编辑**：点击操作列"修改"按钮，可修改用户基本信息和分配角色。
- **删除**：勾选用户后点击"删除"，或点击操作列"删除"按钮。admin 用户不可删除。
- **重置密码**：操作列"更多" → "重置密码"，输入新密码即可。
- **分配角色**：操作列"更多" → "分配角色"，勾选需要的角色。
- **导入/导出**：支持 Excel 批量导入用户和导出用户列表。
- **个人中心**：右上角头像 → 个人中心，可修改昵称、手机、邮箱和头像。

### 角色管理

路径：系统管理 → 角色管理

- **查询**：支持按角色名称、权限字符、状态、创建时间搜索。
- **新增**：填写角色名称、权限字符、排序，并勾选菜单权限。
- **菜单权限**：编辑角色时可勾选该角色能访问的菜单和按钮。
- **数据权限**：操作列"更多" → "数据权限"，设置该角色的数据可见范围（全部/自定义/本部门/本部门及以下/仅本人）。
- **分配用户**：操作列"更多" → "分配用户"，查看和管理该角色下的用户。

### 菜单管理

路径：系统管理 → 菜单管理

- **菜单类型**：目录 (M)、菜单 (C)、按钮 (F) 三种类型。
- **新增目录**：选择上级菜单，类型选"目录"，填写名称和路由地址。
- **新增菜单**：类型选"菜单"，需额外填写组件路径（如 `system/user/index`）和权限字符（如 `system:user:list`）。
- **新增按钮**：类型选"按钮"，只需填写权限字符（如 `system:user:add`），用于控制页面按钮的显示。
- **展开/折叠**：点击工具栏"展开/折叠"按钮可切换树形展示。

### 部门管理

路径：系统管理 → 部门管理

- 树形结构展示组织架构，支持新增、编辑、删除部门。
- 新增时选择上级部门，填写部门名称、负责人、联系方式等。
- 有下级部门的节点不可直接删除，需先删除子部门。

### 岗位管理

路径：系统管理 → 岗位管理

- 维护公司岗位信息（如董事长、项目经理、人力资源、普通员工）。
- 支持按岗位编码、名称、状态搜索。
- 岗位在新增用户时作为下拉选项使用。

### 字典管理

路径：系统管理 → 字典管理

- **字典类型**：定义字典分类（如 `sys_normal_disable` 系统开关、`sys_user_sex` 用户性别）。
- **字典数据**：点击字典类型的"字典数据"按钮，维护该类型下的键值对。
- **缓存刷新**：字典数据缓存在 Redis 中，修改后自动刷新。也可点击工具栏"刷新缓存"手动清除。
- **使用方式**：前端通过 `dict.type.xxx` 引用字典数据，后端通过 `/system/dict/data/type/{dictType}` 接口获取。

### 参数设置

路径：系统管理 → 参数设置

- 维护系统级参数（如是否开启验证码 `sys.account.captchaEnabled`、用户初始密码 `sys.user.initPassword`）。
- 参数缓存在 Redis 中，修改后自动刷新。
- 后端通过 `sys_config` 键名读取参数值。

### 通知公告

路径：系统管理 → 通知公告

- 支持"通知"和"公告"两种类型。
- 内容编辑器支持富文本。
- 支持按标题、操作人员、类型搜索。

### 操作日志

路径：系统管理 → 日志管理 → 操作日志

- 自动记录所有增删改查操作（通过 `@log_operation` 装饰器）。
- 支持按模块、操作类型、操作人员、时间范围搜索。
- 点击操作列可查看请求详情（请求参数、返回结果）。
- 支持导出 Excel 和清空日志。

### 登录日志

路径：系统管理 → 日志管理 → 登录日志

- 记录所有登录/登出操作，包含 IP 地址、浏览器、操作系统信息。
- 支持按登录地址、用户名、状态、时间范围搜索。
- 支持解锁被锁定的账户（连续登录失败 5 次后锁定 10 分钟）。

### 在线用户

路径：系统监控 → 在线用户

- 查看当前所有在线用户的会话信息。
- 支持按登录地址、用户名搜索。
- 点击"强退"可强制踢出用户（从 Redis 中删除其 Token）。

### 定时任务

路径：系统监控 → 定时任务

- **查看任务**：列表展示所有定时任务，包含任务名称、组名、调用目标、cron 表达式、状态。
- **新增任务**：点击"新增"，填写任务名称、调用目标（格式：`模块名.函数名('参数')`）、cron 表达式。
- **启停切换**：点击状态列的开关，确认后启用或暂停任务。
- **立即执行**：操作列"更多" → "执行一次"，不影响任务的定时调度。
- **调度日志**：点击工具栏"日志"按钮查看所有任务的执行记录。

调用目标格式说明：

```
# 无参数
sample_task.no_params

# 单个参数
sample_task.with_params('ry')

# 多个参数
sample_task.with_multi_params('ry', true, 2000)
```

系统会自动从 `app/tasks/` 目录导入对应模块并调用函数。cron 表达式兼容 Quartz 6 位格式（秒 分 时 日 月 周）。

### 数据监控

路径：系统监控 → 数据监控

- 替代 Java 版 Druid 连接池监控页面。
- 展示数据库连接信息（连接地址、ORM 版本）。
- 展示 SQLAlchemy 连接池实时状态（池大小、已签出/签入连接数、溢出连接数）。
- 展示应用信息（Python 版本、FastAPI 版本、调试模式）。
- 刷新页面可获取最新数据。

### 服务监控

路径：系统监控 → 服务监控

- 展示服务器 CPU 使用率、内存使用情况、磁盘状态。
- 展示 JVM（Python 运行时）信息。
- 数据通过 `psutil` 库实时采集。

### 缓存监控

路径：系统监控 → 缓存监控

- 展示 Redis 基本信息（版本、运行模式、端口、内存使用等）。
- 命令统计图表展示各命令的调用次数。
- 内存信息图表展示内存使用占比。

### 缓存列表

路径：系统监控 → 缓存列表

- 按缓存名称分类展示所有 Redis 键（login_tokens、sys_config、sys_dict 等）。
- 点击缓存名称可查看该分类下的所有键名。
- 点击键名可查看缓存内容。
- 支持清理单个键或清理全部缓存。

### 代码生成

路径：系统工具 → 代码生成

- **导入表**：点击"导入"，选择数据库中的表，系统自动读取表结构。
- **编辑配置**：点击"编辑"，可修改生成信息（模块名、业务名、类名）、字段信息（显示类型、查询方式、必填项）。
- **预览代码**：点击"预览"，查看将要生成的 Model、Schema、CRUD、API 代码。
- **生成下载**：勾选表后点击"生成"，下载包含完整 CRUD 代码的 ZIP 包。
- **同步表结构**：当数据库表结构变更后，点击"同步"可更新字段信息。

> 注意：生成的是 Python (FastAPI + SQLAlchemy) 代码，非 Java 代码。

---

## 开发指南：如何添加新功能

本项目采用分层架构，添加新功能只需按照固定模式创建 5 个文件并注册路由。以下以添加一个"产品管理"模块为完整示例。

### 架构分层

```
请求 → API 路由层 → CRUD 数据层 → SQLAlchemy 模型
         ↓               ↓
      Schema 校验    数据库操作
         ↓
      响应格式化
```

| 层 | 目录 | 职责 |
|---|------|------|
| Model | `app/models/` | SQLAlchemy ORM 模型，映射数据库表 |
| Schema | `app/schemas/` | Pydantic 数据校验，处理 camelCase 转换 |
| CRUD | `app/crud/` | 数据库查询逻辑，继承 `CRUDBase` 泛型基类 |
| API | `app/api/` | FastAPI 路由端点，权限校验，响应格式化 |
| Service | `app/services/` | 复杂业务逻辑（可选，简单 CRUD 不需要） |

### 第一步：建表

```sql
CREATE TABLE biz_product (
  product_id   BIGINT       NOT NULL AUTO_INCREMENT,
  product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
  product_code VARCHAR(50)  NOT NULL COMMENT '产品编码',
  price        DECIMAL(10,2) DEFAULT 0 COMMENT '价格',
  status       CHAR(1)      DEFAULT '0' COMMENT '状态（0正常 1停用）',
  create_by    VARCHAR(64)  DEFAULT '',
  create_time  DATETIME     DEFAULT CURRENT_TIMESTAMP,
  update_by    VARCHAR(64)  DEFAULT '',
  update_time  DATETIME     DEFAULT NULL,
  remark       VARCHAR(500) DEFAULT NULL,
  PRIMARY KEY (product_id)
) ENGINE=InnoDB COMMENT='产品表';
```

### 第二步：创建 Model

文件：`app/models/biz_product.py`

```python
from decimal import Decimal
from sqlalchemy import BigInteger, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, AuditMixin


class BizProduct(Base, AuditMixin):
    """产品表。继承 AuditMixin 自动获得 create_by/create_time/update_by/update_time/remark 字段。"""
    __tablename__ = "biz_product"

    product_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    product_code: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    status: Mapped[str] = mapped_column(String(1), default="0")
```

关键点：
- 继承 `Base` 和 `AuditMixin`，自动获得审计字段（create_by、create_time、update_by、update_time、remark）
- 主键使用 `BigInteger` + `autoincrement=True`
- 状态字段用 `String(1)`，`"0"` 表示正常，`"1"` 表示停用（若依约定）

### 第三步：创建 Schema

文件：`app/schemas/biz_product.py`

```python
from decimal import Decimal
from app.schemas import CamelModel


class ProductCreate(CamelModel):
    """新增产品请求体。"""
    product_name: str
    product_code: str
    price: Decimal = Decimal("0")
    status: str = "0"
    remark: str | None = None


class ProductUpdate(CamelModel):
    """修改产品请求体。Update 的 ID 字段必填，其余可选。"""
    product_id: int
    product_name: str | None = None
    product_code: str | None = None
    price: Decimal | None = None
    status: str | None = None
    remark: str | None = None
```

关键点：
- 继承 `CamelModel`，自动支持 camelCase 别名（前端发 `productName`，后端收 `product_name`）
- Create 中必填字段不给默认值，选填字段给默认值
- Update 中除 ID 外所有字段都是 `Optional`，只更新传入的字段

### 第四步：创建 CRUD

文件：`app/crud/crud_product.py`

```python
from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.biz_product import BizProduct
from app.schemas.biz_product import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[BizProduct, ProductCreate, ProductUpdate]):
    """产品 CRUD。继承 CRUDBase 自动获得 get / get_list / create / update / delete_by_ids 方法。"""

    async def get_product_list(
        self,
        db: AsyncSession,
        *,
        page_num: int = 1,
        page_size: int = 10,
        product_name: str | None = None,
        product_code: str | None = None,
        status: str | None = None,
    ) -> tuple[Sequence[BizProduct], int]:
        query = select(BizProduct)
        if product_name:
            query = query.where(BizProduct.product_name.like(f"%{product_name}%"))
        if product_code:
            query = query.where(BizProduct.product_code.like(f"%{product_code}%"))
        if status:
            query = query.where(BizProduct.status == status)
        query = query.order_by(BizProduct.product_id.desc())
        return await self.get_list(db, query=query, page_num=page_num, page_size=page_size)

    async def create_product(self, db: AsyncSession, obj_in: ProductCreate, create_by: str) -> BizProduct:
        product = BizProduct(**obj_in.model_dump(), create_by=create_by)
        db.add(product)
        await db.flush()
        await db.refresh(product)
        return product

    async def update_product(self, db: AsyncSession, obj_in: ProductUpdate, update_by: str) -> BizProduct | None:
        product = await self.get(db, obj_in.product_id)
        if not product:
            return None
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"product_id"})
        update_data["update_by"] = update_by
        update_data["update_time"] = datetime.now()
        for k, v in update_data.items():
            setattr(product, k, v)
        await db.flush()
        return product


crud_product = CRUDProduct(BizProduct)
```

关键点：
- 继承 `CRUDBase[Model, CreateSchema, UpdateSchema]`，自动获得 `get`、`get_list`、`delete_by_ids` 等通用方法
- 列表查询方法构建 `select` 查询，添加过滤条件，调用 `self.get_list()` 自动分页
- 创建时传入 `create_by`，更新时设置 `update_by` 和 `update_time`
- 模块末尾实例化 `crud_product` 供 API 层导入

### 第五步：创建 API 路由

文件：`app/api/biz/product.py`

```python
from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import BusinessType
from app.core.decorators import log_operation
from app.core.deps import has_permi
from app.core.response import AjaxResult, TableDataInfo
from app.crud.crud_product import crud_product
from app.db.session import get_db
from app.schemas.biz_product import ProductCreate, ProductUpdate

router = APIRouter()


def _to_dict(p) -> dict:
    """模型转字典。字段名必须是 camelCase，与前端对应。"""
    return {
        "productId": p.product_id,
        "productName": p.product_name,
        "productCode": p.product_code,
        "price": float(p.price) if p.price else 0,
        "status": p.status,
        "createBy": p.create_by,
        "createTime": p.create_time.strftime("%Y-%m-%d %H:%M:%S") if p.create_time else None,
        "remark": p.remark,
    }


@router.get("/list")
async def list_products(
    current_user: dict = Depends(has_permi("biz:product:list")),
    db: AsyncSession = Depends(get_db),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    productName: str | None = Query(None),
    productCode: str | None = Query(None),
    status: str | None = Query(None),
):
    """分页列表。返回 TableDataInfo 格式。"""
    items, total = await crud_product.get_product_list(
        db, page_num=pageNum, page_size=pageSize,
        product_name=productName, product_code=productCode, status=status,
    )
    return TableDataInfo(total=total, rows=[_to_dict(p) for p in items]).model_dump()


@router.get("/{product_id}")
async def get_product(
    product_id: int,
    current_user: dict = Depends(has_permi("biz:product:query")),
    db: AsyncSession = Depends(get_db),
):
    """获取详情。返回 AjaxResult.success(data=...)。"""
    product = await crud_product.get(db, product_id)
    if not product:
        return AjaxResult.error(msg="产品不存在")
    return AjaxResult.success(data=_to_dict(product))


@router.post("")
@log_operation("产品管理", BusinessType.INSERT)
async def add_product(
    body: ProductCreate,
    request: Request,
    current_user: dict = Depends(has_permi("biz:product:add")),
    db: AsyncSession = Depends(get_db),
):
    """新增。加 @log_operation 装饰器自动记录操作日志。"""
    await crud_product.create_product(db, body, current_user["user_name"])
    return AjaxResult.success()


@router.put("")
@log_operation("产品管理", BusinessType.UPDATE)
async def update_product(
    body: ProductUpdate,
    request: Request,
    current_user: dict = Depends(has_permi("biz:product:edit")),
    db: AsyncSession = Depends(get_db),
):
    await crud_product.update_product(db, body, current_user["user_name"])
    return AjaxResult.success()


@router.delete("/{product_ids}")
@log_operation("产品管理", BusinessType.DELETE)
async def delete_products(
    request: Request,
    product_ids: str = Path(...),
    current_user: dict = Depends(has_permi("biz:product:remove")),
    db: AsyncSession = Depends(get_db),
):
    """批量删除。前端传逗号分隔的 ID 字符串。"""
    ids = [int(i) for i in product_ids.split(",") if i.strip()]
    await crud_product.delete_by_ids(db, ids)
    return AjaxResult.success()
```

关键点：
- `has_permi("biz:product:list")` 权限校验，对应菜单管理中配置的权限字符
- 列表接口返回 `TableDataInfo` 格式：`{code, msg, total, rows}`
- 详情/新增/修改/删除返回 `AjaxResult` 格式：`{code, msg, data}`
- `@log_operation` 装饰器自动记录操作日志，需要 `request` 和 `current_user` 参数
- 删除接口接收逗号分隔的 ID 字符串（若依前端约定）
- `_to_dict` 转换函数中字段名必须是 camelCase

### 第六步：注册路由

文件：`app/api/router.py`

```python
from app.api.biz import product

# 在 api_router 中添加
api_router.include_router(product.router, prefix="/biz/product", tags=["产品管理"])
```

### 第七步：配置菜单权限

在菜单管理中添加：

1. 新增目录：名称"业务管理"，路由地址 `biz`
2. 新增菜单：名称"产品管理"，上级选"业务管理"，路由地址 `product`，组件路径 `biz/product/index`，权限字符 `biz:product:list`
3. 新增按钮权限：
   - 产品查询：`biz:product:query`
   - 产品新增：`biz:product:add`
   - 产品修改：`biz:product:edit`
   - 产品删除：`biz:product:remove`
   - 产品导出：`biz:product:export`

---

## 开发约定与注意事项

### 响应格式

前端统一检查 `res.code !== 200` 判断请求是否成功：

```python
# 成功响应
AjaxResult.success(data={"key": "value"})
# → {"code": 200, "msg": "操作成功", "data": {"key": "value"}}

# 错误响应
AjaxResult.error(msg="产品不存在")
# → {"code": 500, "msg": "产品不存在"}

# 分页列表
TableDataInfo(total=100, rows=[...]).model_dump()
# → {"code": 200, "msg": "查询成功", "total": 100, "rows": [...]}
```

**注意**：数据必须放在 `data` 字段内，不要用 `AjaxResult.success(info=x, rows=y)` 把数据放到顶层。

### camelCase 转换

前端使用 camelCase（`productName`），后端使用 snake_case（`product_name`）。转换通过两处实现：

1. **Schema 层**：继承 `CamelModel`，自动接受 camelCase 输入
2. **API 层**：`_to_dict` 函数手动输出 camelCase 字段名

### 权限控制

```python
# 需要登录即可访问
current_user: dict = Depends(get_current_user)

# 需要特定权限
current_user: dict = Depends(has_permi("biz:product:list"))

# 需要特定角色
current_user: dict = Depends(has_role("admin"))
```

### 操作日志

在需要记录日志的端点上添加装饰器：

```python
from app.core.constants import BusinessType
from app.core.decorators import log_operation

@router.post("")
@log_operation("产品管理", BusinessType.INSERT)  # 模块名, 操作类型
async def add_product(
    body: ProductCreate,
    request: Request,          # 必须有 request 参数
    current_user: dict = ...,  # 必须有 current_user 参数
    db: AsyncSession = ...,
):
```

操作类型常量：`OTHER=0, INSERT=1, UPDATE=2, DELETE=3, GRANT=4, EXPORT=5, IMPORT=6, FORCE=7, GENCODE=8, CLEAN=9`

### 路由顺序

FastAPI 按注册顺序匹配路由。如果有 `/{id}` 这样的路径参数路由，必须把具体路由放在前面：

```python
# 正确顺序
@router.get("/list")          # 先匹配具体路由
@router.get("/export")
@router.get("/{product_id}")  # 最后匹配通配路由

# 错误顺序（/list 会被 /{product_id} 捕获）
@router.get("/{product_id}")
@router.get("/list")          # 永远不会被匹配到
```

### 添加定时任务

1. 在 `app/tasks/` 目录下创建模块文件：

```python
# app/tasks/my_task.py
import logging

logger = logging.getLogger(__name__)

async def clean_expired_data():
    """清理过期数据。"""
    logger.info("开始清理过期数据...")
    # 你的业务逻辑
    logger.info("清理完成")
```

2. 在前端"定时任务"页面新增任务，调用目标填写：`my_task.clean_expired_data`
3. 填写 cron 表达式（6 位 Quartz 格式），如 `0 0 2 * * ?` 表示每天凌晨 2 点执行

### 添加字典数据

1. 在前端"字典管理"中新增字典类型（如 `biz_product_status`）
2. 添加字典数据（如 `0=正常, 1=停用`）
3. 前端组件中使用：`<dict-tag :options="dict.type.biz_product_status" :value="scope.row.status"/>`

---

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
│   │   ├── monitor/           # 系统监控 (operlog, logininfor, online, server, cache, job, job_log, druid)
│   │   ├── tool/              # 系统工具 (gen 代码生成)
│   │   └── common.py          # 通用接口 (文件上传)
│   ├── models/                # SQLAlchemy ORM 模型
│   │   ├── base.py            # 声明基类 + AuditMixin 审计字段
│   │   ├── associations.py    # 多对多关联表
│   │   ├── sys_*.py           # 各业务表模型
│   │   └── gen_table.py       # 代码生成表模型
│   ├── schemas/               # Pydantic 请求/响应数据模型 (CamelModel 基类支持驼峰别名)
│   ├── crud/                  # 数据访问层 (CRUDBase 泛型基类 + 各业务 CRUD)
│   ├── services/              # 业务逻辑层 (auth_service, menu_service, codegen_service, job_service)
│   ├── tasks/                 # 定时任务函数 (APScheduler 调用目标)
│   ├── core/                  # 核心模块
│   │   ├── security.py        # JWT 令牌 + bcrypt 密码加密
│   │   ├── deps.py            # FastAPI 依赖注入 (当前用户、权限校验)
│   │   ├── data_scope.py      # 数据权限过滤
│   │   ├── decorators.py      # 操作日志装饰器
│   │   ├── redis.py           # Redis 连接管理
│   │   ├── middleware.py      # CORS 等中间件
│   │   ├── response.py        # 统一响应格式 (AjaxResult, TableDataInfo)
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

---

## 已测试页面

以下页面已通过完整的 CRUD 功能测试（含新增、编辑、删除、查询等操作）：

| 模块 | 页面 | 状态 |
|------|------|------|
| 系统管理 | 用户管理 | 通过 |
| 系统管理 | 角色管理 | 通过 |
| 系统管理 | 菜单管理 | 通过 |
| 系统管理 | 部门管理 | 通过 |
| 系统管理 | 岗位管理 | 通过 |
| 系统管理 | 字典管理 | 通过 |
| 系统管理 | 参数设置 | 通过 |
| 系统管理 | 通知公告 | 通过 |
| 系统监控 | 操作日志 | 通过 |
| 系统监控 | 登录日志 | 通过 |
| 系统监控 | 在线用户 | 通过 |
| 系统监控 | 服务监控 | 通过 |
| 系统监控 | 缓存监控 | 通过 |
| 系统监控 | 缓存列表 | 通过 |
| 系统监控 | 定时任务 | 通过 |
| 系统监控 | 调度日志 | 通过 |
| 系统监控 | 数据监控 | 通过 |
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
