#!/usr/bin/env bash

celery -A "src.queues.app" beat -S "src.queues.scheduler:DatabaseScheduler" -l info
