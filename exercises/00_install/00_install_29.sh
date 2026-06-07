#!/bin/bash -eu
# Security is disabled: plain HTTP, no credentials needed.

# Basic health check
curl -X GET "http://localhost:9200/_cluster/health?pretty"

# Get cluster information
curl -X GET "http://localhost:9200"

# List indices
curl -X GET "http://localhost:9200/_cat/indices?v"
