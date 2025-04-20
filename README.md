<div align="center">
  <h1>Async-FastAPI-MultiDB</h1>
  <span>中文 | <a href="./README-EN.md">English</a></span>
</div>

Async-FastAPI-MultiDB 是一个异步 FastAPI 模板项目，旨在无缝集成 SQL (如 PostgreSQL, MySQL) 和 NoSQL (如 MongoDB) 数据库。该模板提供了一种现代化且高效的 Web 框架解决方案，支持异步请求处理，非常适合用于构建可扩展的 API 服务。

---

## 特点
- **异步架构：** 全面支持 `async/await` 提高性能。
- **SQL & NoSQL 集成：** 支持 SQLModel/SQLAlchemy（MySQL 和 PostgreSQL等关系型数据库）以及 Beanie（基于 MongoDB 的 ODM），可同时使用关系型数据库和文档数据库，满足多种数据存储需求。
- **模块化设计：** 采用清晰的项目结构，将路由、模型、服务层、数据库操作等功能解耦，便于维护和扩展，可适应大型项目开发。
- **自动文档生成：** 利用 FastAPI 内置功能自动生成 API 文档。
- **基于环境的配置管理：** 简化不同环境下的配置切换。
- **对象存储系统 MinIO：** MinIO 是一个开源的分布式对象存储系统，兼容 Amazon S3 API，支持通过 S3 协议与国内云服务（如阿里云、腾讯云）进行集成。
  - 如果你曾使用 boto3，推荐切换到 MinIO 提供的 Python SDK，它更加现代、智能，并且优化了性能和易用性。
  - 本项目封装了一些常用的 S3 接口功能，例如：获取预签名上传链接、支持分块上传、生成下载地址、获取存储桶信息等。
  - 更多细节请参考 `src.utils.minio_client.py` 文件中的实现。
- **Celery 增强功能（[更多详情](#celery)）：**
  - 数据库动态调度（类似 `django-celery-beat`，但与框架无关）
  - 异步任务原生支持（自动兼容 `async def` 函数）
  - 更友好的 IDE 类型提示（改善开发体验)
- **认证与授权功能，基于 JWT + Redis + RSA 实现([详细说明](#Auth-模块说明))：**
  - 使用 JWT 区分 Access Token 与 Refresh Token
  - 登录密码通过 RSA 加密传输，提升安全性
  - 依赖注入基于类型注解，便于统一管理与功能扩展

> 🚧 本项目持续开发中，欢迎关注、Star 或提出 Issue 与 PR。

---

## 安装
1. 克隆仓库：
    ```bash
    git clone https://github.com/GJCoke/Async-FastAPI-MultiDB.git
    cd Async-FastAPI-MultiDB
    ```
2. 复制环境变量信息：
    ```bash
    cp .env.example .env
    ```
3. 运行Docker
    ```bash
    docker network create app_network
    docker compose up -d --build
    ```
4. 初始化数据库
   1. 运行 Alembic 创建数据库结构
      ```bash
      docker compose exec app scripts/alembic-makemigrations.sh "Init Database"
      docker compose exec app scripts/alembic-migrate.sh
      ```
   2. 运行 initdb 脚本生成初始数据
      ```bash
      docker compose exec app scripts/initdb.sh
      ```

5. 开发
   本项目使用 `pre-commit` 来确保代码在提交前的质量和一致性。它会在代码提交前自动运行检查工具和格式化工具。
    ```bash
    pre-commit install
    ```
   > `pre-commit` 的配置文件是 `.pre-commit-config.yaml`，其中包含以下钩子：
   > - 大文件检查：提交的代码中是否添加了过大的文件。
   > - 代码格式化：使用 ruff 自动格式化代码。
   > - 静态代码检查：使用 mypy 进行静态代码检查。

> 访问 [http://localhost:16000/docs](http://localhost:16000/docs) 即可查看 Swagger 文档
#### 示例1
![swagger-1](docs/images/swagger-1.png)
#### 示例2
> 错误响应已统一增强处理，无需在每个路由中单独添加错误响应。

![swagger-2](docs/images/swagger-2.png)
---

## Auth 模块说明

本模块用于处理认证授权相关功能，基于 JWT + Redis + RSA 实现。

### 功能概述

- 用户登录（用户名密码）
- AccessToken / RefreshToken 生成与校验
- Token 刷新
- Token 登出
- 用户信息注入依赖封装
- 环境限制依赖（Debug）

### 密码加密（RSA）

> 无需担心添加 RSA 后 Swagger 文档无法使用，因为 Swagger 文档有独立的登录逻辑，并且该逻辑仅在 DEBUG 环境下生效。

登录时前端使用后端提供的 RSA 公钥加密密码，后端使用私钥解密。
保证密码传输过程中不会明文暴露。

>
> 密钥对建议由环境配置提供。
>
> 当前 `DEBUG` 环境支持动态生成, 但是不推荐在部署环境中使用。
>
> 在多个服务或实例中使用动态生成会导致不一致的行为，特别是在负载均衡或分布式缓存（如 Redis）等情况下。

### Token 说明

- **AccessToken:** 短效，存在客户端，用于接口鉴权
- **RefreshToken:** 长效，存在 Redis，支持刷新操作

> RefreshToken 内嵌 `jti`（唯一标识）与 `User-Agent`，确保每次刷新来源一致。

### 核心依赖

| 名称                      | 说明                             |
|-------------------------|--------------------------------|
| `HeaderAccessTokenDep`  | 获取 Header 中的 AccessToken       |
| `HeaderRefreshTokenDep` | 获取 Header 中的 RefreshToken      |
| `HeaderUserAgentDep`    | 获取 Header 中的 User-Agent        |
| `UserAccessJWTDep`      | 解码 AccessToken 后的用户信息          |
| `UserRefreshJWTDep`     | 解码 RefreshToken 并校验 User-Agent |
| `AuthCrudDep`           | 数据库操作封装，用于获取用户信息               |
| `UserRefreshDep`        | 从 Redis + DB 校验并获取用户信息         |
| `UserDBDep`             | 从 DB 获取用户信息                    |

### 路由简述

- `GET /keys/public`：获取用于加密密码的RSA公钥
- `POST /login`：用户登录，返回 access_token 和 refresh_token
- `POST /token/refresh`：刷新 token，需携带 refresh_token 和 User-Agent
- `POST /logout`：登出，删除 Redis 中的 refresh_token
- `GET /user/info`：获取用户信息

### Redis 结构

- 存储 Key： `auth:refresh:<{user_id}>:<{jti}>`
- 存储 Value：RefreshToken（含 `created_at`, `refresh_token`, `user-agent` 等）

> 可扩展如：添加 IP 地址校验、添加设备 ID / 平台标识、限制刷新来源、控制多端登录策略

> 所有依赖和逻辑均通过类型注解与 FastAPI 自动注入实现，便于复用与扩展。

---

## Celery

### DatabaseScheduler — 数据库动态调度器
通过自定义调度器 `DatabaseScheduler`，实现从数据库中动态加载周期任务，并支持定时自动刷新：

- 类似 `django-celery-beat`，但可自由集成于任意 Web 框架（FastAPI）
- 周期性地（如每 60 秒）从数据库加载任务，无需重启 Worker
- 自动合并配置文件中的任务，优先使用配置项
- 支持 `AsyncSession` `asyncpg` 你无需再向之前一样提供一个同步的数据库

#### 示例代码
```python
from src.core.config import settings
from src.queues.celery import Celery

REDIS_URL = str(settings.CELERY_REDIS_URL)
DATABASE_URL = "postgresql+asyncpg://your_username:your_password@localhost:27017/you_database"
app = Celery("celery_app", broker=REDIS_URL, backend=REDIS_URL)
app.conf.update({"timezone": settings.CELERY_TIMEZONE, "database_url": DATABASE_URL, "refresh_interval": 60})

app.autodiscover_tasks(["src.queues.tasks"])
```

运行 Celery beat `celery -A "src.queues.app" beat -S "src.queues.scheduler:AsyncDatabaseScheduler" -l info`

### AsyncTask — 原生支持 async def 的任务
通过自定义 Task 基类，让 Celery 支持异步任务的自动识别与执行：

- 如果任务是 async def，自动使用 asyncio.run() 或当前事件循环运行
- 无需手动区分 sync / async，统一任务调用逻辑
- 完全兼容已有的同步任务

#### 示例代码
```python
import asyncio

from src.queues.app import app


@app.task
async def run_async_task() -> None:
    print("async task start.")
    await asyncio.sleep(10)
    print("async task done.")
```

运行 Celery worker `celery -A "src.queues.app" worker -l info`

### TypedCelery — 增强类型提示的 Celery 封装
对原生 Celery 进行了封装，以获得更精准的类型提示支持：

- 重写了 Celery 部分函数和类，使返回值和函数签名在 IDE 中更加明确
- 在 PyCharm、VSCode 中智能提示参数与返回值，减少低级错误
- 对新手或大型项目尤其友好，提升团队开发效率
#### 示例1
![celery-type-1](docs/images/celery-type-1.png)
#### 示例2
![celery-type-2](docs/images/celery-type-2.png)
#### 示例3
![celery-type-3](docs/images/celery-type-3.png)

> 更多细节请参考 `src.queues` 目录中的源代码，了解任务注册、调度器实现以及异步任务的执行逻辑。

---

## Git 相关规范
见 <span><a href="./docs/GIT.md">Git 规范</a></span>

---

## 许可证
本项目基于 Apache-2.0 许可证，详见 [LICENSE](LICENSE) 文件。

---
