#!/bin/bash -eu
# Install Elasticsearch
sudo apt install -y elasticsearch

# These exercises run with security DISABLED, so the generated password and
# enrollment token shown during installation are not needed. Security is
# turned off in the configuration step below.
