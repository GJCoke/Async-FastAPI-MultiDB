"""
Author  : Coke
Date    : 2025-04-07
"""

import time

from celery import Celery

REDIS_URL = "redis://:123456@localhost:36379/0"
celery = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)
celery.conf.timezone = "Asia/Shanghai"

celery.conf.beat_schedule = {
    "polling_task": {
        "task": "src.worker.periodic_query",  # 任务路径
        "schedule": 10.0,  # 每10秒执行一次任务
    },
}


@celery.task
def query_task_status(task_id: int) -> None:
    print("这是测试任务: {}".format(task_id))
    time.sleep(1)
    print("任务结束了.")


@celery.task
def periodic_query() -> None:
    # TODO: get task iss
    task_ids = [1, 2, 3, 4]

    for task_id in task_ids:
        query_task_status.apply_async(args=(task_id,))
