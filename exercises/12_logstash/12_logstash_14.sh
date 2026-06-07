#!/bin/bash
# Monitor index growth
watch -n 5 'curl -s "localhost:9200/_cat/indices?v" | grep system-logs'

# Count documents
curl -X GET "localhost:9200/system-logs-*/_count?pretty"

# Get latest entries
curl -X GET "localhost:9200/system-logs-*/_search?pretty&size=1" -H 'Content-Type: application/json' -d'
{
  "query": { "match_all": {} },
  "sort": [{ "@timestamp": { "order": "desc" }}]
}'
