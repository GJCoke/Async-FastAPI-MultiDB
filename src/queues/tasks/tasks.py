"""
Celery tasks.
Author  : Coke
Date    : 2025-04-10
"""

import asyncio
import random

from src.queues.app import app


@app.task
async def test_celery() -> None:  # TODO: this is delete code.
    print("start celery task ...")
    random_number = random.randint(1, 10)
    print(f"task run {random_number}s.")
    # time.sleep(random_number)
    await asyncio.sleep(random_number)

    async def test_async() -> None:
        print("start async task ...")
        print(f"async task run {random_number}s.")
        await asyncio.sleep(random_number)

    await test_async()

    print("task done.")
