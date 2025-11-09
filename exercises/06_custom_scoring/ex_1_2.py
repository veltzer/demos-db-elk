#!/bin/env python

from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Boost by popularity (view_count)
def search_with_popularity_boost(query_text):
    query = {
        "query": {
            "function_score": {
                "query": {
                    "match": {
                        "description": query_text
                    }
                },
                "field_value_factor": {
                    "field": "view_count",
                    "factor": 1.2,
                    "modifier": "log1p",  # log1p, log, ln, square, sqrt, reciprocal
                    "missing": 1
                },
                "boost_mode": "multiply"  # multiply, sum, avg, first, max, min
            }
        },
        "size": 5
    }

    result = es.search(index="products", body=query)

    print(f"\nSearch: \"{query_text}\" with popularity boost")
    print("-" * 50)
    for hit in result["hits"]["hits"]:
        product = hit["_source"]
        print(f"Score: {hit['_score']:.2f} | Views: {product['view_count']} | {product['name']}")

# Test popularity boosting
search_with_popularity_boost("quality features")
