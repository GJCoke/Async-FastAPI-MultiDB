#!/bin/sh -e

coverage run -m --source=src pytest -s tests/

coverage html
