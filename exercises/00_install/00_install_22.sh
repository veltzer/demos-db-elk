#!/bin/bash
# With Elasticsearch security disabled, no enrollment token is required.
# Kibana connects to Elasticsearch over plain HTTP with no credentials.
# Edit the configuration as needed:
nano /opt/elastic/kibana/config/kibana.yml
# Set: server.host: "0.0.0.0"
# Set: elasticsearch.hosts: ["http://localhost:9200"]
