#!/bin/bash -eu
curl -X POST "localhost:9200/_query?format=txt" -H 'Content-Type: application/json' -d'
{
  "query": "FROM orders | EVAL line_total = price * quantity | STATS total_spent = SUM(line_total) BY customer | SORT total_spent DESC | LIMIT 3"
}'
