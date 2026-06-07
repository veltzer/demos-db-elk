#!/bin/bash -eu
# Start in detached mode
podman compose up -d

# View logs
podman compose logs -f

# Check container status
podman compose ps
