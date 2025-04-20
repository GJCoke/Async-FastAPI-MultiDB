# get just list.
default:
  just --list

# cp env file.
cp env:
  cp .env.example .env

# run static check.
format:
   docker compose exec app scripts/static-check.sh

# stop docker compose
stop:
  docker compose stop

# start up docker compose
up:
  docker compose up -d

# build docker compose
build:
  docker compose up -d --build

# kill docker compose
kill:
  docker compose kill

# get docker compose list
ps:
  docker compose ps

# Run Alembic database migrations
migrate:
  docker compose exec app scripts/alembic-migrate.sh

# Downgrade the database to a previous version with optional arguments
downgrade *args:
  docker compose exec app scripts/alembic-downgrade.sh {{args}}

# Generate new Alembic migration files with optional arguments
makemigrations *args:
  docker compose exec app scripts/alembic-makemigrations.sh {{args}}

# init database.
initdb:
  docker compose exec app scripts/initdb.sh
