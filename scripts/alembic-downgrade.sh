#!/bin/sh -e

# Rollback the database to a specified version.
alembic downgrade "$1"
