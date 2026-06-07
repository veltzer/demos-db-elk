#!/bin/bash
# Delete single document
curl -X DELETE "localhost:9200/products/_doc/1"

# Delete by query
curl -X POST "localhost:9200/products/_delete_by_query" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "term": {
        "in_stock": false
      }
    }
  }'

# Delete entire index
curl -X DELETE "localhost:9200/products"
