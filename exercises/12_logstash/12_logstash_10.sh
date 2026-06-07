#!/bin/bash
# Get some log entries
curl -X GET "localhost:9200/system-logs-*/_search?pretty&size=5" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match_all": {}
  },
  "sort": [
    { "@timestamp": { "order": "desc" } }
  ]
}'
