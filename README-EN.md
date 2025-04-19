<div align="center">
	<h1>Async-FastAPI-MultiDB</h1>
  <span><a href="./README.md">中文</a> | English</span>
</div>

Async-FastAPI-MultiDB is an asynchronous FastAPI project template designed to seamlessly integrate both SQL (e.g., PostgreSQL, MySQL) and NoSQL (e.g., MongoDB) databases. This modern and efficient web framework is ideal for building scalable API services with full async support.

---

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
- **Authentication & Authorization powered by JWT + Redis + RSA ([Details](#Auth-Module-Overview)):**
  - Uses JWT to distinguish between Access and Refresh Tokens
  - Passwords are encrypted using RSA for secure transmission
  - Fully type-annotated dependencies with FastAPI for easy reuse and extensibility

> 🚧 This project is under active development. Feel free to follow, star the repo, or contribute via issues and PRs.

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
## Auth Module Overview

This module handles authentication and authorization, built upon JWT + Redis + RSA.

### Features Overview

- User login via username and password
- AccessToken / RefreshToken generation and validation
- Token refresh
- Token logout
- Encapsulated user info injection via dependency
- Environment-based restrictions (e.g., Debug-only features)

### Password Encryption (RSA)

> You don't need to worry about Swagger UI being affected by RSA encryption — it uses an independent login flow, which only works in the `DEBUG` environment.

During login, the frontend encrypts the password using the RSA public key provided by the backend. The backend then decrypts it using the private key, ensuring that the password is never transmitted in plain text.

> It is recommended to configure the key pair via environment variables.
>
> The `DEBUG` environment supports dynamic key generation, but this is not recommended in production.
>
> Dynamic keys can lead to inconsistent behavior across multiple services or instances, especially in environments with load balancing or distributed caching (e.g., Redis).

### Token Description

- **AccessToken:** Short-lived, stored on the client, used for authenticating API requests
- **RefreshToken:** Long-lived, stored in Redis, used to refresh access tokens

> The RefreshToken embeds a unique `jti` (JWT ID) and `User-Agent` to ensure the refresh request originates from the same source.

### Core Dependencies

| 名称                      | 说明                                                     |
|-------------------------|--------------------------------------------------------|
| `HeaderAccessTokenDep`  | Extracts the AccessToken from the request header       |
| `HeaderRefreshTokenDep` | Extracts the RefreshToken from the request header      |
| `HeaderUserAgentDep`    | Extracts the User-Agent from the request header        |
| `UserAccessJWTDep`      | Decodes the AccessToken and retrieves user information |
| `UserRefreshJWTDep`     | Decodes the RefreshToken and validates the User-Agent  |
| `AuthCrudDep`           | CRUD wrapper for user-related database operations      |
| `UserRefreshDep`        | Validates and retrieves user info via Redis + Database |
| `UserDBDep`             | Retrieves user information directly from the database  |

### Route Summary
- `GET /keys/public`: Retrieve the RSA public key used for encrypting passwords
- `POST /login`: User login, returns both access_token and refresh_token
- `POST /token/refresh`: Refresh the token, requires refresh_token and User-Agent
- `POST /logout`: Logout, deletes the refresh token from Redis
- `GET /user/info`: Retrieve current user information

### Redis Structure
- Stored Key: auth:refresh:<{user_id}>:<{jti}>
- Stored Value: A serialized RefreshToken object, including fields like created_at, refresh_token, and user-agent

> This structure is extensible — you can include IP address verification, device ID, platform identifier, restrict refresh sources, or implement multi-device login control strategies.

> All dependencies and logic are injected via type annotations and FastAPI’s dependency system, making them easy to reuse and extend.

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

---

## Git Commit Convention
See <span><a href="./docs/GIT-EN.md">Git Guidelines</a></span>

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
