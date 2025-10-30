#!/usr/bin/env python

from elasticsearch import Elasticsearch
from datetime import datetime

# Connect to Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Delete index if it exists
if es.indices.exists(index="dynamic_test"):
    es.indices.delete(index="dynamic_test")

# Aggregation on keyword field
agg_result = es.search(
    index="static_test",
    body={
        "size": 0,
        "aggs": {
            "popular_tags": {
                "terms": {
                    "field": "tags",
                    "size": 10
                }
            },
            "avg_score": {
                "avg": {
                    "field": "score"
                }
            },
            "active_count": {
                "value_count": {
                    "field": "is_active"
                }
            }
        }
    }
)

print("Aggregation Results:")
print(f"Popular tags: {agg_result["aggregations"]["popular_tags"]["buckets"]}")
print(f"Average score: {agg_result["aggregations"]["avg_score"]["value"]}")
print(f"Active users count: {agg_result["aggregations"]["active_count"]["value"]}")
