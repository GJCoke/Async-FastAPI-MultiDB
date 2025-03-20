<div align="center">
	<h1>Async-FastAPI-MultiDB</h1>
  <span>中文 | <a href="./README-EN.md">English</a></span>
</div>

Async-FastAPI-MultiDB 是一个异步 FastAPI 模板项目，旨在无缝集成 SQL (如 PostgreSQL, MySQL) 和 NoSQL (如 MongoDB) 数据库。该模板提供了一种现代化且高效的 Web 框架解决方案，支持异步请求处理，非常适合用于构建可扩展的 API 服务。

## 特点
- **异步架构：** 全面支持 `async/await` 提高性能。
- **SQL & NoSQL 集成：** 支持 SQLAlchemy 和 Motor 用于数据库操作。
- **模块化设计：** 清晰且易于维护的代码结构，便于扩展。
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
    docker network create fastapi_multi_async_network
    docker compose up -d --build
```
4. 本地运行(安装依赖)
```bash
    pip install ".[dev]"
    uvicorn --reload "src.main:app"
```

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

## 许可证
本项目基于 Apache-2.0 许可证，详见 [LICENSE](LICENSE) 文件。

