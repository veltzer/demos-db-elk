#!/bin/bash
# Test Elasticsearch (security disabled: plain HTTP, no credentials)
curl -X GET "http://localhost:9200"

# Check container status
docker compose ps

# Access Kibana (security disabled: no login required)
echo "Open browser: http://localhost:5601"
