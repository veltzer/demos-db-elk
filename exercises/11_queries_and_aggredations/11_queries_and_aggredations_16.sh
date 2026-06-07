#!/bin/bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": {
      "customer": "Alice"
    }
  },
  "aggs": {
    "alice_categories": {
      "terms": {
        "field": "category"
      }
    }
  }
}'
