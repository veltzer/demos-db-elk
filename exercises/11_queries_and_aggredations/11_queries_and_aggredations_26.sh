#!/bin/bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "avg_order_per_customer": {
      "terms": {
        "field": "customer"
      },
      "aggs": {
        "avg_order_value": {
          "avg": { "field": "price" }
        }
      }
    }
  }
}'
