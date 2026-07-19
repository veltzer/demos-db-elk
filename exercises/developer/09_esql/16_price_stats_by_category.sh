#!/bin/bash -eu
curl -X POST "localhost:9200/_query?format=txt" -H 'Content-Type: application/json' -d'
{
  "query": "FROM orders | STATS order_count = COUNT(*), min_price = MIN(price), max_price = MAX(price), avg_price = ROUND(AVG(price), 2) BY category | SORT avg_price DESC"
}'
