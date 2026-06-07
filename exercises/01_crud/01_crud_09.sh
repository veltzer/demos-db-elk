#!/bin/bash -eu
# Authentication failed / 401 errors:
# These exercises run Elasticsearch with security DISABLED, so no username
# or password is required. Do NOT pass -u credentials or use https.
# Connect over plain HTTP with no authentication:
curl -X GET "http://localhost:9200"
