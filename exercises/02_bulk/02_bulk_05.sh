#!/bin/bash
# Check Elasticsearch is running
systemctl status elasticsearch

# Test connection
curl -X GET "http://localhost:9200"
