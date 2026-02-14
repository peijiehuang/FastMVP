# RuoYi-FastAPI

基于 Python FastAPI 框架重新实现的 [若依(RuoYi-Vue)](https://gitee.com/y_project/RuoYi-Vue) 后台管理系统后端。搭配适配版前端 [FastMVPVueUI](https://github.com/peijiehuang/FastMVPVueUI) 可开箱即用，无需修改前端代码。

> **前端说明：** 本项目配套的前端 [FastMVPVueUI](https://github.com/peijiehuang/FastMVPVueUI) 基于若依官方 Vue2 前端修改，已适配代码生成模块（Python 语法高亮、预览标签等），可直接使用。如使用若依官方原版前端，需自行做少量修改，详见 [前端修改说明](#前端修改说明)。

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
# 后端
git clone https://github.com/peijiehuang/FastMVP.git
cd FastMVP

# 前端（另开目录）
git clone https://github.com/peijiehuang/FastMVPVueUI.git
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

# Redis 连接 (无密码)
REDIS_URL=redis://localhost:6379/0
# Redis 连接 (有密码，注意密码前的冒号，用户名留空)
# REDIS_URL=redis://:your_redis_password@localhost:6379/0

# JWT 密钥 (生产环境务必修改为随机字符串)
JWT_SECRET=your-secret-key-change-in-production

# Token 过期时间 (分钟)
TOKEN_EXPIRE_MINUTES=30

# 验证码开关 (设为 false 可关闭登录验证码)
CAPTCHA_ENABLED=true
```

### 5. 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8090 --reload
```

启动成功后可访问：

| 地址 | 说明 |
|------|------|
| http://localhost:8090/docs | Swagger UI 交互式 API 文档 |
| http://localhost:8090/redoc | ReDoc 风格 API 文档 |
| http://localhost:8090/health | 健康检查接口 |

### 6. 前端对接

使用适配版前端 [FastMVPVueUI](https://github.com/peijiehuang/FastMVPVueUI)：

```bash
cd FastMVPVueUI
npm install
npm run dev
```

前端默认代理已指向 `http://localhost:8090`，启动后端后直接访问前端即可。

如需修改代理地址，编辑 `vue.config.js`：

```javascript
// vue.config.js
devServer: {
  proxy: {
    '/dev-api': {
      target: 'http://localhost:8090',
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

## 开发指南

本项目采用分层架构，添加新功能有两种方式：

1. **代码生成器（推荐）** -- 通过前端页面导入数据库表，一键生成 Model / Schema / CRUD / API 骨架代码，再手动完善业务逻辑
2. **手动编写** -- 按照固定模式逐层创建文件，适合需要高度定制的场景

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

### 方式一：使用代码生成器（推荐）

代码生成器可以从已有数据库表自动生成 Model、Schema、CRUD、API 四层代码，省去手写样板代码的工作。

#### 第一步：建表

在 MySQL 中创建业务表，遵循若依命名约定：

```sql
CREATE TABLE biz_product (
  product_id   BIGINT       NOT NULL AUTO_INCREMENT COMMENT '产品ID',
  product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
  product_code VARCHAR(50)  NOT NULL COMMENT '产品编码',
  price        DECIMAL(10,2) DEFAULT 0 COMMENT '价格',
  status       CHAR(1)      DEFAULT '0' COMMENT '状态（0正常 1停用）',
  create_by    VARCHAR(64)  DEFAULT '' COMMENT '创建者',
  create_time  DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  update_by    VARCHAR(64)  DEFAULT '' COMMENT '更新者',
  update_time  DATETIME     DEFAULT NULL COMMENT '更新时间',
  remark       VARCHAR(500) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (product_id)
) ENGINE=InnoDB COMMENT='产品表';
```

#### 第二步：导入表并生成代码

1. 打开前端页面：系统工具 → 代码生成
2. 点击 **导入** 按钮，在弹窗中勾选 `biz_product` 表，点击确定
3. 点击 **编辑** 按钮，可修改生成信息：
   - 基本信息：模块名（`biz`）、业务名（`product`）、功能名（`产品管理`）、作者
   - 字段信息：调整每个字段的显示类型（输入框/下拉框/日期等）、是否必填、查询方式（精确/模糊）
4. 点击 **预览** 可查看将要生成的 4 个文件
5. 勾选表后点击 **生成** 按钮，下载 ZIP 包

#### 第三步：放置生成的文件

解压 ZIP 包，将 4 个文件放到对应目录：

```
biz_product/
├── model.py   → 复制到 app/models/biz_product.py
├── schema.py  → 复制到 app/schemas/biz_product.py
├── crud.py    → 复制到 app/crud/crud_product.py
└── api.py     → 复制到 app/api/biz/product.py
```

#### 第四步：完善生成的代码

生成的代码是骨架，API 层的端点标记了 `# TODO`，需要补充实际业务逻辑。以下是需要完善的要点：

**model.py** -- 调整列类型

生成器默认所有非主键字段为 `String(255)`，需要根据实际表结构修改：

```python
# 生成的代码（所有字段都是 String）
product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
price: Mapped[str | None] = mapped_column(String(255), nullable=True)

# 修改后（匹配实际数据库类型）
product_name: Mapped[str] = mapped_column(String(100), nullable=False)
price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
```

**schema.py** -- 改用 CamelModel

生成的 Schema 继承 `BaseModel`，需改为 `CamelModel` 以支持前端 camelCase 字段名：

```python
# 生成的代码
from pydantic import BaseModel
class BizProductCreate(BaseModel): ...

# 修改后
from app.schemas import CamelModel
class BizProductCreate(CamelModel): ...
```

**crud.py** -- 添加列表查询方法

生成的 CRUD 类是空的，继承了 `CRUDBase` 的通用方法。需要添加带过滤条件的分页查询：

```python
class CRUDBizProduct(CRUDBase[BizProduct, BizProductCreate, BizProductUpdate]):
    async def get_product_list(
        self, db: AsyncSession, *, page_num=1, page_size=10,
        product_name: str | None = None, status: str | None = None,
    ) -> tuple[Sequence[BizProduct], int]:
        query = select(BizProduct)
        if product_name:
            query = query.where(BizProduct.product_name.like(f"%{product_name}%"))
        if status:
            query = query.where(BizProduct.status == status)
        query = query.order_by(BizProduct.product_id.desc())
        return await self.get_list(db, query=query, page_num=page_num, page_size=page_size)
```

**api.py** -- 填充 TODO 端点

生成的 API 端点都是 `# TODO` 占位，需要接入 CRUD 层并添加权限校验、操作日志、响应格式化：

```python
from app.core.deps import has_permi          # 替换 get_current_user
from app.core.decorators import log_operation # 操作日志
from app.core.constants import BusinessType

@router.get("/list")
async def list_product(
    current_user: dict = Depends(has_permi("biz:product:list")),  # 权限校验
    db: AsyncSession = Depends(get_db),
    pageNum: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    productName: str | None = Query(None),
):
    items, total = await crud_product.get_product_list(
        db, page_num=pageNum, page_size=pageSize, product_name=productName,
    )
    return TableDataInfo(total=total, rows=[_to_dict(p) for p in items]).model_dump()

@router.post("")
@log_operation("产品管理", BusinessType.INSERT)  # 记录操作日志
async def add_product(
    body: BizProductCreate,
    request: Request,
    current_user: dict = Depends(has_permi("biz:product:add")),
    db: AsyncSession = Depends(get_db),
):
    product = BizProduct(**body.model_dump(), create_by=current_user["user_name"])
    db.add(product)
    await db.flush()
    return AjaxResult.success()
```

别忘了添加 `_to_dict()` 函数将模型转为 camelCase 字典：

```python
def _to_dict(p) -> dict:
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
```

#### 第五步：注册路由

在 `app/api/router.py` 中添加：

```python
from app.api.biz import product
api_router.include_router(product.router, prefix="/biz/product", tags=["产品管理"])
```

#### 第六步：配置菜单权限

在前端 系统管理 → 菜单管理 中添加：

1. 新增目录：名称 `业务管理`，路由地址 `biz`
2. 新增菜单：名称 `产品管理`，上级选 `业务管理`，路由 `product`，组件 `biz/product/index`，权限 `biz:product:list`
3. 新增按钮权限：`biz:product:query` / `biz:product:add` / `biz:product:edit` / `biz:product:remove` / `biz:product:export`

#### 生成代码 vs 手动编写对照

| 内容 | 生成器自动完成 | 需要手动完善 |
|------|---------------|-------------|
| Model 基本结构 | ✅ 类名、表名、字段 | 列类型精确映射（默认全是 String） |
| Schema | ✅ Create/Update 字段 | 改继承 CamelModel、调整必填/类型 |
| CRUD | ✅ 继承 CRUDBase | 添加带过滤条件的列表查询方法 |
| API 路由 | ✅ 5 个端点骨架 | 填充业务逻辑、权限校验、操作日志 |
| 路由注册 | ❌ | 手动在 router.py 中注册 |
| 菜单权限 | ❌ | 手动在前端菜单管理中配置 |

### 方式二：手动编写（完整控制）

如果需要更精细的控制，可以跳过代码生成器，手动创建每一层文件。完整示例参考方式一中各层的"修改后"代码，按以下顺序创建：

1. **建表** -- 在 MySQL 中创建业务表
2. **Model** -- `app/models/biz_product.py`，继承 `Base` + `AuditMixin`
3. **Schema** -- `app/schemas/biz_product.py`，继承 `CamelModel`，定义 Create/Update
4. **CRUD** -- `app/crud/crud_product.py`，继承 `CRUDBase`，添加列表查询方法
5. **API** -- `app/api/biz/product.py`，定义路由端点，添加权限校验和操作日志
6. **注册路由** -- 在 `app/api/router.py` 中 `include_router`
7. **配置菜单** -- 在前端菜单管理中添加目录、菜单、按钮权限

### 添加后台服务（定时任务）

系统使用 APScheduler 3.x 实现定时任务调度，支持 Quartz 6 位 cron 表达式，任务函数放在 `app/tasks/` 目录下。

#### 编写任务函数

在 `app/tasks/` 目录下创建 Python 模块，每个函数就是一个可调度的任务：

```python
# app/tasks/my_task.py
import logging

logger = logging.getLogger(__name__)


def sync_data():
    """同步数据（同步函数）。"""
    logger.info("开始同步数据...")
    # 你的业务逻辑
    logger.info("同步完成")


async def clean_expired_data(days: int = 30):
    """清理过期数据（异步函数，支持参数）。"""
    logger.info(f"清理 {days} 天前的过期数据...")
    # 你的业务逻辑（可以使用 await）
    logger.info("清理完成")


def send_report(email: str, include_chart: bool = True):
    """发送报表（多参数）。"""
    logger.info(f"发送报表到 {email}, 包含图表: {include_chart}")
```

任务函数支持同步和异步两种写法，调度器会自动识别。

#### 注册任务

在前端 系统监控 → 定时任务 页面点击"新增"，填写：

| 字段 | 说明 | 示例 |
|------|------|------|
| 任务名称 | 任务描述 | 清理过期数据 |
| 任务组名 | 分组（DEFAULT/SYSTEM） | DEFAULT |
| 调用目标 | `模块名.函数名(参数)` | `my_task.clean_expired_data(90)` |
| cron 表达式 | Quartz 6 位格式 | `0 0 2 * * ?` |
| 执行策略 | 错过触发时的处理 | 放弃执行 |
| 是否并发 | 同一任务是否允许并行 | 禁止 |

#### 调用目标格式

调用目标的格式为 `模块名.函数名(参数列表)`，系统自动从 `app/tasks/` 目录导入对应模块：

```
# 无参数
my_task.sync_data

# 单个参数
my_task.clean_expired_data(90)

# 多个参数（支持字符串、数字、布尔值）
my_task.send_report('admin@example.com', true)
```

参数使用 `ast.literal_eval` 安全解析，支持 Python 字面量（字符串、数字、布尔值、None、列表、字典）。布尔值可以用 `true/false`（自动转换为 Python 的 `True/False`）。

#### cron 表达式

使用 Quartz 6 位格式：`秒 分 时 日 月 周`

| 表达式 | 含义 |
|--------|------|
| `0 0 2 * * ?` | 每天凌晨 2:00 |
| `0 */5 * * * ?` | 每 5 分钟 |
| `0 0 9 ? * MON-FRI` | 工作日早上 9:00 |
| `0/10 * * * * ?` | 每 10 秒 |
| `0 0 12 1 * ?` | 每月 1 号中午 12:00 |

`?` 表示不指定（日和周互斥时使用），系统会自动转换为 APScheduler 兼容格式。

#### 任务管理

- **启停切换**：点击状态列开关，暂停后任务不再触发，恢复后按 cron 继续调度
- **立即执行**：操作列"更多" → "执行一次"，立即触发一次，不影响定时调度
- **调度日志**：点击工具栏"日志"按钮，查看每次执行的结果、耗时和异常信息
- **并发控制**：设为"禁止"时，上一次执行未完成则跳过本次触发

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

以下页面已通过完整的功能测试，每个模块均验证了所有可用操作：

| 模块 | 页面 | 测试项 | 状态 |
|------|------|--------|------|
| 系统管理 | 用户管理 | 查询 / 新增 / 编辑 / 删除 | ✅ 通过 |
| 系统管理 | 角色管理 | 查询 / 新增 / 编辑 / 删除 | ✅ 通过 |
| 系统管理 | 菜单管理 | 查询 / 新增 / 编辑 / 删除 | ✅ 通过 |
| 系统管理 | 部门管理 | 查询 / 新增 / 编辑 / 删除 | ✅ 通过 |
| 系统管理 | 岗位管理 | 查询 / 新增 / 编辑 / 删除 | ✅ 通过 |
| 系统管理 | 字典管理 | 查询 / 新增 / 编辑 / 删除 | ✅ 通过 |
| 系统管理 | 参数设置 | 查询 / 新增 / 编辑 / 删除 | ✅ 通过 |
| 系统管理 | 通知公告 | 查询 / 新增 / 编辑 / 删除 | ✅ 通过 |
| 系统管理 | 操作日志 | 查询 / 详细 / 删除 / 清空 | ✅ 通过 |
| 系统管理 | 登录日志 | 查询 / 删除 / 清空 | ✅ 通过 |
| 系统监控 | 在线用户 | 查询 | ✅ 通过 |
| 系统监控 | 定时任务 | 查询 / 新增 / 编辑 / 删除 / 启停 / 执行一次 | ✅ 通过 |
| 系统监控 | 调度日志 | 查询 / 删除 / 清空 | ✅ 通过 |
| 系统监控 | 数据监控 | 查看连接池状态 | ✅ 通过 |
| 系统监控 | 服务监控 | 查看 CPU/内存/磁盘 | ✅ 通过 |
| 系统监控 | 缓存监控 | 查看 Redis 信息/命令统计/内存 | ✅ 通过 |
| 系统监控 | 缓存列表 | 查看缓存分类 / 键名列表 / 缓存内容 | ✅ 通过 |
| 系统工具 | 代码生成 | 查询 / 导入表 / 预览代码 / 删除 | ✅ 通过 |

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
| 9 | 操作日志/登录日志清空返回 500 | `api/monitor/operlog.py`, `api/monitor/logininfor.py` | `/clean` 路由定义在 `/{ids}` 之后，"clean" 被当作路径参数解析导致 `int("clean")` 失败 |
| 10 | 操作日志清空请求超时 | `api/monitor/operlog.py` | `@log_operation` 装饰器在独立 session 中 INSERT 日志，而主 session 的 DELETE 未提交持有表锁，形成死锁。移除清空端点的 `@log_operation` 装饰器解决 |

## 前端修改说明

> **推荐直接使用适配版前端 [FastMVPVueUI](https://github.com/peijiehuang/FastMVPVueUI)，以下修改已内置，无需手动操作。**

如果使用若依官方原版前端 `ruoyi-ui`，需要对代码生成预览页面做以下修改：

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
