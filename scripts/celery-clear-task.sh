#!/usr/bin/env bash

celery -A "src.queues.app" purge -f