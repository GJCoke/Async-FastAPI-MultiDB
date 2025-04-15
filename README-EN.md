<div align="center">
	<h1>Async-FastAPI-MultiDB</h1>
  <span><a href="./README.md">中文</a> | English</span>
</div>

Async-FastAPI-MultiDB is an asynchronous FastAPI project template designed to seamlessly integrate both SQL (e.g., PostgreSQL, MySQL) and NoSQL (e.g., MongoDB) databases. This modern and efficient web framework is ideal for building scalable API services with full async support.

## Features

- **Asynchronous Architecture:** Fully utilizes `async/await` to maximize performance.
- **SQL & NoSQL Support:** Built-in support for SQLModel/SQLAlchemy (for relational databases like MySQL and PostgreSQL) and Beanie (an ODM for MongoDB), allowing hybrid data storage.
- **Modular Project Structure:** Well-organized with separation of concerns across routers, models, services, and database operations. Easy to scale and maintain for large projects.
- **Auto API Documentation:** Automatically generated via FastAPI’s built-in OpenAPI support.
- **Environment-based Configuration:** Simplified switching between different deployment environments.
- **Object Storage with MinIO:** MinIO is an open-source distributed object storage system compatible with the Amazon S3 API. It can be easily integrated with Chinese cloud providers (e.g., Alibaba Cloud, Tencent Cloud).
  - Compared to `boto3`, MinIO’s Python SDK offers a more modern, intelligent, and performant experience.
  - This project encapsulates several commonly used S3 API features, such as generating presigned upload URLs, supporting multipart uploads, creating download links, and retrieving bucket information.
  - For more details, please refer to the implementation in `src.utils.minio_client.py`.
- **Enhanced Celery Integration (see [Celery](#celery)):**
  - Dynamic database scheduling (similar to `django-celery-beat` but framework-agnostic)
  - Native async task support (`async def`)
  - Better type hinting in IDEs for improved development experience

🚧 This project is under active development. Feel free to follow, star the repo, or contribute via issues and PRs.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/GJCoke/Async-FastAPI-MultiDB.git
    cd Async-FastAPI-MultiDB
    ```

2. Copy the environment variables:
    ```bash
    cp .env.example .env
    ```

3. Run with Docker:
    ```bash
    docker network create app_network
    docker compose up -d --build
    ```
    Access the Swagger UI at: [http://localhost:16000/docs](http://localhost:16000/docs)

4. Run locally:
    ```bash
    pip install ".[dev]"
    uvicorn --reload "src.main:app"
    ```
    Access the Swagger UI at: [http://localhost:8000/docs](http://localhost:8000/docs)

5. Development workflow:
    This project uses `pre-commit` to enforce code quality and consistency:
    ```bash
    pre-commit install
    ```

    The `.pre-commit-config.yaml` includes:
    - Auto formatting via `ruff`
    - Static type checking with `mypy`

---

## Usage

1. Create and apply migrations for SQL databases (e.g., PostgreSQL):
    ```bash
    alembic revision --autogenerate -m "Init Database"
    alembic upgrade head
    ```

2. Start the server:
    ```bash
    uvicorn src.main:app --reload
    ```

3. Access the API docs:
    ```
    http://127.0.0.1:8000/docs
    ```

---

## Celery
For more details, please refer to the source code in the `src.queues` directory, including task registration, scheduler implementation, and async task execution logic.

### DatabaseScheduler — Dynamic Database-based Scheduler

The custom `DatabaseScheduler` dynamically loads periodic tasks from the database, refreshing at configurable intervals:

- Works like `django-celery-beat` but framework-agnostic (built for FastAPI)
- Loads tasks periodically (e.g., every 60 seconds) without restarting workers
- Automatically merges with configuration-defined tasks
- Fully async compatible via `AsyncSession` and `asyncpg`

#### Example
```python
from src.core.config import settings
from src.queues.celery import Celery

REDIS_URL = str(settings.CELERY_REDIS_URL)
DATABASE_URL = "postgresql+asyncpg://your_username:your_password@localhost:27017/your_database"

app = Celery("celery_app", broker=REDIS_URL, backend=REDIS_URL)
app.conf.update({"timezone": settings.CELERY_TIMEZONE, "database_url": DATABASE_URL, "refresh_interval": 60})

app.autodiscover_tasks(["src.queues.tasks"])
```
Run beat with: `celery -A "src.queues.app" beat -S "src.queues.scheduler:AsyncDatabaseScheduler" -l info`

AsyncTask — Native Async Task Support
Our custom task base class auto-detects async def functions and handles execution:

- Automatically runs async def tasks in the proper event loop
- No need to manually distinguish between sync and async tasks
- Backward compatible with sync tasks

#### Example
```python
import asyncio
from src.queues.app import app

@app.task
async def run_async_task() -> None:
    print("async task start.")
    await asyncio.sleep(10)
    print("async task done.")

```
Run worker with: `celery -A "src.queues.app" worker -l info`

#### TypedCelery — IDE-Friendly Celery Wrapper
Enhances native Celery with improved type hinting and IDE integration:

- Refactored class definitions to return accurate types
- Enables smart autocomplete and error detection in IDEs like PyCharm or VSCode
- Greatly improves development speed and reduces bugs in large teams
#### Example 1
![celery-type-1](docs/images/celery-type-1.png)
#### Example 2
![celery-type-2](docs/images/celery-type-2.png)
#### Example 3
![celery-type-3](docs/images/celery-type-3.png)

## Git Commit Convention
See <span><a href="./docs/GIT-EN.md">Git Guidelines</a></span>

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
