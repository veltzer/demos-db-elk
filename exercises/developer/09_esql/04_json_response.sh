#!/bin/bash -eu
curl -X POST "localhost:9200/_query?pretty" -H 'Content-Type: application/json' -d'
{
  "query": "FROM orders | LIMIT 10"
}'
