#!/bin/bash -eu
curl -X POST "localhost:9200/_query?format=txt" -H 'Content-Type: application/json' -d'
{
  "query": "FROM orders | WHERE status == \"pending\" | KEEP customer, product, price, status"
}'
