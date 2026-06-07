#!/bin/bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "total_sales": {
      "sum": {
        "field": "price"
      }
    }
  }
}'
