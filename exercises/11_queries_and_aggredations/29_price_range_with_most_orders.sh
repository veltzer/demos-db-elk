#!/bin/bash -eu
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [
          { "key": "$0-25", "from": 0, "to": 25 },
          { "key": "$25-100", "from": 25, "to": 100 },
          { "key": "$100+", "from": 100 }
        ]
      }
    }
  }
}'
