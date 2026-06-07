#!/bin/bash
# Basic health check
curl -X GET "https://localhost:9200/_cluster/health?pretty" -k -u elastic:<password>

# Get cluster information
curl -X GET "https://localhost:9200" -k -u elastic:<password>

# List indices
curl -X GET "https://localhost:9200/_cat/indices?v" -k -u elastic:<password>
