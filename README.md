<div align="center">
	<h1>Async-FastAPI-MultiDB</h1>
  <span><a href="./README-EN.md">English</a> | 中文</span>
</div>

Async-FastAPI-MultiDB 是一个异步 FastAPI 模板项目，旨在无缝集成 SQL (如 PostgreSQL, MySQL) 和 NoSQL (如 MongoDB) 数据库。该模板提供了一种现代化且高效的 Web 框架解决方案，支持异步请求处理，非常适合用于构建可扩展的 API 服务。

## 特点
- **异步架构：** 全面支持 `async/await` 提高性能。
- **SQL & NoSQL 集成：** 支持 SQLModel/SQLAlchemy（MySQL 和 PostgreSQL等关系型数据库）以及 Beanie（基于 MongoDB 的 ODM），可同时使用关系型数据库和文档数据库，满足多种数据存储需求。
- **模块化设计：** 采用清晰的项目结构，将路由、模型、服务层、数据库操作等功能解耦，便于维护和扩展，可适应大型项目开发。
- **自动文档生成：** 利用 FastAPI 内置功能自动生成 API 文档。
- **基于环境的配置管理：** 简化不同环境下的配置切换。

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
3. 使用Docker
    ```bash
    docker network create app_network
    docker compose up -d --build
    ```
   访问 `http://localhost:16000/docs` 即可查看 Swagger 文档

4. 本地运行(安装依赖)
    ```bash
    pip install ".[dev]"
    uvicorn --reload "src.main:app"
    ```
   访问 `http://localhost:8000/docs` 即可查看 Swagger 文档
5. 开发

    本项目使用 `pre-commit` 来确保代码在提交前的质量和一致性。它会在代码提交前自动运行检查工具和格式化工具。
    ```bash
    pre-commit install
    ```
    `pre-commit` 的配置文件是 `.pre-commit-config.yaml`，其中包含以下钩子：
    - 代码格式化：使用 ruff 自动格式化代码。

## 使用方法
1. 为 SQL 数据库（如 PostgreSQL）创建并应用迁移：
    ```bash
    alembic upgrade head
    ```
2. 运行服务器：
    ```bash
    uvicorn main:app --reload
    ```
3. 访问自动生成的文档：
    ```
    http://127.0.0.1:8000/docs
    ```

## Git 相关规范
<span><a href="./docs/GIT.md">Git 规范</a></span>

## 许可证
本项目基于 Apache-2.0 许可证，详见 [LICENSE](LICENSE) 文件。
