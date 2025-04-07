#!/bin/sh -e

# Generate the specified migration file with the migration content $1.
alembic revision --autogenerate -m "$1"
