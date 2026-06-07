#!/bin/bash -eu
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "term": { "customer": "Bob" } },
        { "term": { "status": "delivered" } }
      ]
    }
  }
}'
