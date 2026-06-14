#!/bin/bash -eu
# Install Kibana
sudo apt install -y kibana

# With Elasticsearch security disabled, no enrollment token is required.
# Kibana connects to Elasticsearch over plain HTTP with no credentials.
# Optionally edit the configuration for external access:
sudo nano /etc/kibana/kibana.yml
# Set: server.host: "0.0.0.0" for external access
# Set: elasticsearch.hosts: ["http://localhost:9200"]
