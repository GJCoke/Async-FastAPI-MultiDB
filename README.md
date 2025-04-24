<div align="center">
  <h1>Async-FastAPI-MultiDB</h1>
  <span>English | <a href="./README-CN.md">中文</a></span>
</div>

This is a production-ready asynchronous backend template built with FastAPI, featuring integrated support for Celery, JWT authentication, RBAC permissions, and MinIO object storage. It supports both MongoDB and PostgreSQL, making it a powerful and flexible choice for modern backend development.

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
- **Authentication & Authorization powered by JWT + Redis + RSA + RBAC ([Details](#Auth-Module-Overview)):**
  - Uses JWT to distinguish between Access and Refresh Tokens
  - Passwords are encrypted using RSA for secure transmission
  - Fully type-annotated dependencies with FastAPI for easy reuse and extensibility
  - Route-based RBAC Permission System
  - High-performance Permission Validation Mechanism

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

4. Run Alembic to create the database schema.
    ```bash
    docker compose exec app scripts/alembic-makemigrations.sh "Initialize Database"
    docker compose exec app scripts/alembic-migrate.sh
    ```
5. Run the initdb script to generate the necessary initial data.
    ```bash
    docker compose exec app scripts/initdb.sh
    ```

6. Development workflow:
    This project uses `pre-commit` to enforce code quality and consistency:
    ```bash
    pre-commit install
    ```

    > The `.pre-commit-config.yaml` includes:
    > - Large file check: Whether large files have been added to the committed code.
    > - Auto formatting via `ruff`
    > - Static type checking with `mypy`

> Access the Swagger UI at: [http://localhost:16000/docs](http://localhost:16000/docs)
#### Example 1
![swagger-1](docs/images/swagger-1.png)
#### Example 2
> Error responses are globally enhanced—no need to define them on each route individually.

![swagger-2](docs/images/swagger-2.png)
---

---
## Auth Module Overview

This module handles authentication and authorization, built upon JWT + Redis + RSA + RBAC.

### Features Overview

- User login via username and password
- AccessToken / RefreshToken generation and validation
- Token refresh
- Token logout
- Encapsulated user info injection via dependency
- Environment-based restrictions (e.g., Debug-only features)
- RBAC access control model

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

### RBAC
- No need to manually define permission codes for each API endpoint; the system automatically generates and matches permission identifiers based on the endpoint path and HTTP method, achieving fully automated permission management.
- User permission data is stored in Redis as structured data and cached according to the access-token lifecycle, effectively reducing database lookups and greatly improving permission-check efficiency and overall system response speed.


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
| `VerifyPermissionDep`   | Route-based User Access Permission Validation          |

### Route Summary
- `GET /keys/public`: Retrieve the RSA public key used for encrypting passwords
- `POST /login`: User login, returns both access_token and refresh_token
- `POST /token/refresh`: Refresh the token, requires refresh_token and User-Agent
- `POST /logout`: Logout, deletes the refresh token from Redis
- `GET /user/info`: Retrieve current user information
- `GET /router/backend`：Get Application Routes

### Redis Structure
- Stored Key: `auth:refresh:<{user_id}>:<{jti}>`
- Stored Value: A serialized RefreshToken object, including fields like `created_at`, `refresh_token`, and `user-agent`
- Stored Key: `auth:permission:<{user_id}>`
- Stored Value: Current user's permission code

> This structure is extensible — you can include IP address verification, device ID, platform identifier, restrict refresh sources, or implement multi-device login control strategies.

> All dependencies and logic are injected via type annotations and FastAPI’s dependency system, making them easy to reuse and extend.

---

## Celery

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

> For more details, please refer to the source code in the `src.queues` directory, including task registration, scheduler implementation, and async task execution logic.

---

## Git Commit Convention
See <span><a href="./docs/GIT.md">Git Guidelines</a></span>

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
