#!/bin/bash
# Check if processes are running
ps aux | grep elasticsearch
ps aux | grep kibana

# Test Elasticsearch (security disabled: plain HTTP, no credentials)
curl -X GET "http://localhost:9200"

# Access Kibana (security disabled: no login required)
echo "Open browser: http://localhost:5601"
