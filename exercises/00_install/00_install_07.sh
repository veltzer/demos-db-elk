#!/bin/bash
# Test Elasticsearch (replace <password> with your elastic user password)
# with security
curl -X GET "https://localhost:9200" -k -u elastic:<password>
# without security
curl -X GET "http://localhost:8200"

# Access Kibana
# with security
echo "Open browser: https://localhost:5601"
echo "Login with username: elastic"
echo "Password: <the password from Elasticsearch installation>"
# without security
echo "Open browser: http://localhost:5601"
