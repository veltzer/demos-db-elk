#!/bin/bash
# Test Elasticsearch
# with security
curl -X GET "https://localhost:9200" -k -u elastic:changeme123
# without security
curl -X GET "http://localhost:8200"

# Check container status
docker compose ps

# Access Kibana
# with security
echo "Open browser: https://localhost:5601"
# without security
echo "Open browser: http://localhost:5601"
echo "Login with username: elastic"
echo "Password: changeme123"
