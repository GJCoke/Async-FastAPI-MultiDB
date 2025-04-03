#!/usr/bin/env bash

set -e

# Create a folder to store logs.
LOG_DIR="logs"
if [[ ! -d "$LOG_DIR" ]]; then
  mkdir -p "$LOG_DIR"
fi

# FastAPI application entry point.
DEFAULT_MODULE_NAME=src.main

# Application configuration, using default values if none are provided.
MODULE_NAME=${MODULE_NAME:-$DEFAULT_MODULE_NAME}
VARIABLE_NAME=${VARIABLE_NAME:-app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

# Log and port configuration, using default values if none are provided.
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8006}
LOG_LEVEL=${LOG_LEVEL:-info}
LOG_CONFIG=${LOG_CONFIG:-logging.ini}

# Start the server.
exec uvicorn --reload --proxy-headers --host $HOST --port $PORT --log-config $LOG_CONFIG "$APP_MODULE"
