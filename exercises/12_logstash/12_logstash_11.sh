#!/bin/bash -eu
# Search for auth logs
curl -X GET "localhost:9200/system-logs-*/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": {
      "type": "auth"
    }
  }
}'
