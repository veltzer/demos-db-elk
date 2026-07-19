#!/bin/bash -eu
curl -X POST "localhost:9200/_query?format=txt" -H 'Content-Type: application/json' -d'
{
  "query": "FROM orders | EVAL line_total = price * quantity | SORT line_total DESC | LIMIT 5 | KEEP customer, product, quantity, line_total"
}'
