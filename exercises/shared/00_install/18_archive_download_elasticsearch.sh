#!/bin/bash -eu
# Download Elasticsearch
sudo wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-9.1.3-linux-x86_64.tar.gz

# Extract archive
sudo tar -xzf elasticsearch-9.1.3-linux-x86_64.tar.gz

# Create symbolic link for easier access
sudo ln -s elasticsearch-9.1.3 elasticsearch

# Set ownership
sudo chown -R $USER:$USER /opt/elastic/elasticsearch-9.1.3
