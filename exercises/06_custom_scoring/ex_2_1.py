#!/bin/env python

from elasticsearch import Elasticsearch
from datetime import datetime

es = Elasticsearch(["http://localhost:9200"])

# Boost recent products using Gaussian decay
def search_with_recency_boost(query_text):
    query = {
        "query": {
            "function_score": {
                "query": {
                    "match": {
                        "description": query_text
                    }
                },
                "functions": [
                    {
                        "gauss": {
                            "created_date": {
                                "origin": "now",
                                "scale": "30d",  # Half decay at 30 days
                                "offset": "7d",   # No decay for first 7 days
                                "decay": 0.5
                            }
                        },
                        "weight": 2
                    }
                ],
                "boost_mode": "multiply"
            }
        },
        "size": 5
    }

    result = es.search(index="products", body=query)

    print(f"\nRecency-boosted search: \"{query_text}\"")
    print("-" * 50)
    for hit in result["hits"]["hits"]:
        p = hit["_source"]
        days_old = (datetime.now() - datetime.fromisoformat(p["created_date"].replace("Z", "+00:00"))).days
        print(f"Score: {hit['_score']:.2f} | Age: {days_old} days | {p['name']}")

search_with_recency_boost("product features")
