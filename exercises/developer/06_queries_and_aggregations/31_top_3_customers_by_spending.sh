#!/bin/bash -eu
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "top_customers": {
      "terms": {
        "field": "customer",
        "size": 3,
        "order": {
          "total_spent": "desc"
        }
      },
      "aggs": {
        "total_spent": {
          "sum": {
            "field": "price"
          }
        }
      }
    }
  }
}'
