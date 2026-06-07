#!/bin/bash
curl -X PUT "localhost:9200/orders?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "customer": { "type": "keyword" },
      "product": { "type": "text" },
      "category": { "type": "keyword" },
      "price": { "type": "float" },
      "quantity": { "type": "integer" },
      "date": { "type": "date" },
      "status": { "type": "keyword" }
    }
  }
}'
