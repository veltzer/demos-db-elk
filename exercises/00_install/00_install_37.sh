#!/bin/bash
# Navigate to project directory
cd ~/elastic-podman

# Stop and remove containers
podman compose down

# Remove volumes (WARNING: This deletes all data!)
podman compose down -v

# Remove images (optional)
podman rmi docker.elastic.co/elasticsearch/elasticsearch:9.1.3
podman rmi docker.elastic.co/kibana/kibana:9.1.3

# Remove project directory
cd ~ && rm -rf ~/elastic-podman
