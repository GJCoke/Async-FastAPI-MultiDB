"""
Author  : Coke
Date    : 2025-04-10
"""

import random
import time

from src.queues.app import app


@app.task  # type: ignore
def test_celery() -> None:  # TODO: this is delete code.
    print("start celery task ...")
    random_number = random.randint(1, 10)
    print(f"task run {random_number}s.")
    time.sleep(random_number)
    print("task done.")
