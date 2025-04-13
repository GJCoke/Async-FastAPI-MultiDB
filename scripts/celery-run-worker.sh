#!/usr/bin/env bash

celery -A "src.queues.app" worker -l info
