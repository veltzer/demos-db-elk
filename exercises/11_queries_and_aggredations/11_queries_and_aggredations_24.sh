#!/bin/bash -eu
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "term": { "category": "Electronics" } },
        { "range": { "price": { "lt": 200 } } }
      ]
    }
  },
  "aggs": {
    "total_electronics_sales": {
      "sum": { "field": "price" }
    }
  }
}'
