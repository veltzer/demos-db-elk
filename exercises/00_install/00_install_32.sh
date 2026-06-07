#!/bin/bash
# Install Podman (Debian/Ubuntu)
sudo apt update
sudo apt install -y podman

# Verify Podman and the compose provider are available
podman --version
podman compose version
