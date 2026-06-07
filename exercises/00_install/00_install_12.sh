#!/bin/bash -eu
# Start in detached mode
docker compose up -d

# View logs
docker compose logs -f

# Wait for services to be healthy
docker compose ps
