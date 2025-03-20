#!/usr/bin/env bash

set -e

# 创建日志存放文件夹
LOG_DIR="logs"
if [[ ! -d "$LOG_DIR" ]]; then
  mkdir -p "$LOG_DIR"
fi

# FastAPI 应用程序启动入口
DEFAULT_MODULE_NAME=src.main

# 应用信息配置, 无传递则取默认值
MODULE_NAME=${MODULE_NAME:-$DEFAULT_MODULE_NAME}
VARIABLE_NAME=${VARIABLE_NAME:-app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

# 日志及端口配置, 无传递则取默认值
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8006}
LOG_LEVEL=${LOG_LEVEL:-info}
LOG_CONFIG=${LOG_CONFIG:-logging.ini}

# 启动服务器 --reload 在 Mac 下会一直检测到变化
exec uvicorn --reload --proxy-headers --host $HOST --port $PORT --log-config $LOG_CONFIG "$APP_MODULE"