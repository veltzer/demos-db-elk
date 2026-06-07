#!/bin/bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "orders_per_day": {
      "date_histogram": {
        "field": "date",
        "calendar_interval": "day"
      }
    }
  }
}'
