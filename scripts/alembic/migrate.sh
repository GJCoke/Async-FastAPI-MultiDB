#!/bin/sh -e

# Migrate the database to the latest version.
alembic upgrade head
