#!/bin/bash -eu
# Check if Elasticsearch is running
curl -X GET "localhost:9200"

# Check if you're using the correct port and protocol
# Default is http://localhost:9200, not https
