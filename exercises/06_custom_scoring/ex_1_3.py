#!/bin/env python

from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Combine multiple scoring factors
def multi_factor_search(query_text):
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
                        "field_value_factor": {
                            "field": "rating",
                            "factor": 2,
                            "modifier": "square",
                            "missing": 1
                        },
                        "weight": 3
                    },
                    {
                        "field_value_factor": {
                            "field": "review_count",
                            "factor": 1.5,
                            "modifier": "log1p",
                            "missing": 0
                        },
                        "weight": 2
                    },
                    {
                        "filter": {"term": {"is_featured": True}},
                        "weight": 5
                    },
                    {
                        "filter": {"range": {"stock_quantity": {"gt": 0}}},
                        "weight": 2
                    }
                ],
                "score_mode": "sum",  # sum, avg, first, max, min, multiply
                "boost_mode": "multiply",
                "max_boost": 10
            }
        },
        "size": 5,
        "explain": False  # Set to True to see scoring details
    }

    result = es.search(index="products", body=query)

    print(f"\nMulti-factor search: \"{query_text}\"")
    print("-" * 60)
    print(f"{'Score':<10} {'Rating':<8} {'Reviews':<10} {'Featured':<10} {'Name'}")
    print("-" * 60)

    for hit in result["hits"]["hits"]:
        p = hit["_source"]
        featured = "Yes" if p["is_featured"] else "No"
        print(f"{hit['_score']:<10.2f} {p['rating']:<8.1f} {p['review_count']:<10} {featured:<10} {p['name'][:30]}")

multi_factor_search("excellent value")
