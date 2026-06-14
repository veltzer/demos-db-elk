#!/bin/bash -eu
# Check Kibana API status
curl -X GET "http://localhost:5601/api/status"

# Verify in browser
# Navigate to: http://localhost:5601 or http://<your-server-ip>:5601
# You should see the Kibana login page
