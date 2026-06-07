#!/bin/bash
# Check if processes are running
ps aux | grep elasticsearch
ps aux | grep kibana

# Test Elasticsearch
curl -X GET "https://localhost:9200" -k -u elastic:<your-password>

# Access Kibana
echo "Open browser: http://localhost:5601"
echo "Login with username: elastic"
echo "Password: <password from Elasticsearch startup>"
