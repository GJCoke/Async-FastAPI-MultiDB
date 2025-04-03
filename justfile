# get just list.
default:
  just --list

# cp env file.
cp env:
  cp .env.example .env

# run static check.
static check:
  sh ./scripts/static-check.sh

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
