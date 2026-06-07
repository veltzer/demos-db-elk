#!/bin/bash
# Delete single document
curl -X DELETE "localhost:9200/products/_doc/1" \
  -u elastic:your-password

# Delete by query
curl -X POST "localhost:9200/products/_delete_by_query" \
  -H 'Content-Type: application/json' \
  -u elastic:your-password \
  -d '{
    "query": {
      "term": {
        "in_stock": false
      }
    }
  }'

# Delete entire index
curl -X DELETE "localhost:9200/products" \
  -u elastic:your-password
