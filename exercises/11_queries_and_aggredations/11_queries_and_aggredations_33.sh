#!/bin/bash
# Extended price statistics with percentiles.
# NOTE: This block was truncated/corrupt in the original answers.md
# (it ended mid-array). Completed here to a runnable percentiles aggregation.
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "price_percentiles": {
      "percentiles": {
        "field": "price",
        "percents": [25, 50, 75, 95, 99]
      }
    }
  }
}'
