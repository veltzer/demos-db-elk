#!/bin/bash -eu
curl -X POST "localhost:9200/_query?format=txt" -H 'Content-Type: application/json' -d'
{
  "query": "FROM orders | EVAL line_total = price * quantity | KEEP customer, product, price, quantity, line_total"
}'
