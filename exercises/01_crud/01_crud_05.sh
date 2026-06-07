#!/bin/bash
# Get specific document
curl -X GET "localhost:9200/products/_doc/1?pretty" \
  -u elastic:your-password

# Search all documents
curl -X GET "localhost:9200/products/_search?pretty" \
  -H 'Content-Type: application/json' \
  -u elastic:your-password \
  -d '{
    "query": {
      "match_all": {}
    }
  }'

# Search with criteria
curl -X GET "localhost:9200/products/_search?pretty" \
  -H 'Content-Type: application/json' \
  -u elastic:your-password \
  -d '{
    "query": {
      "bool": {
        "must": [
          { "match": { "category": "Electronics" } },
          { "range": { "price": { "gte": 50, "lte": 300 } } }
        ]
      }
    }
  }'

# Simple query string search
curl -X GET "localhost:9200/products/_search?q=category:Electronics&pretty" \
  -u elastic:your-password
