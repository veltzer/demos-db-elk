#!/bin/bash -eu
curl -X POST "localhost:9200/_query?format=txt" -H 'Content-Type: application/json' -d'
{
  "query": "FROM orders | WHERE category == \"Electronics\" | STATS order_count = COUNT(*), avg_price = ROUND(AVG(price), 2)"
}'
