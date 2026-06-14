#!/bin/bash -eu
# Check if processes are running (|| true so a no-match grep doesn't abort under -e)
ps aux | grep elasticsearch || true
ps aux | grep kibana || true

# Test Elasticsearch (security disabled: plain HTTP, no credentials)
curl -X GET "http://localhost:9200"

# Access Kibana (security disabled: no login required)
echo "Open browser: http://localhost:5601"
