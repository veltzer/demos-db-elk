#!/bin/bash -eu
# Navigate to project directory
cd ~/elastic-docker

# Stop and remove containers
docker compose down

# Remove volumes (WARNING: This deletes all data!)
docker compose down -v

# Remove images (optional)
docker rmi docker.elastic.co/elasticsearch/elasticsearch:9.1.3
docker rmi docker.elastic.co/kibana/kibana:9.1.3

# Remove project directory
cd ~ && rm -rf ~/elastic-docker
