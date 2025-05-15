#!/bin/sh -e
set -x

TARGET_DIR=${1:-src}

# ruff format
ruff check --fix "$TARGET_DIR"
ruff format "$TARGET_DIR"

# mypy static type check
mypy "$TARGET_DIR"
