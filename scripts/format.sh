#!/bin/sh -e
set -x

TARGET_DIR=${1:-src}

# 格式化代码
ruff check --fix "$TARGET_DIR"
ruff format "$TARGET_DIR"
