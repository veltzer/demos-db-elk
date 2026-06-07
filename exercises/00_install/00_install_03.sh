#!/bin/bash
# Install Elasticsearch
sudo apt install -y elasticsearch

# IMPORTANT: Save the generated password and enrollment token shown during installation!
# If you miss it, reset the password:
sudo /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic
