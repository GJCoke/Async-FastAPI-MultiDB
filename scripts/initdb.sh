#!/usr/bin/env bash

set -e

export PYTHONPATH=${PYTHONPATH:-/src}

python src/initdb.py
