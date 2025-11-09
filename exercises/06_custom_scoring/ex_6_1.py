#!/bin/env python

from elasticsearch import Elasticsearch
import time

es = Elasticsearch(["http://localhost:9200"])

def compare_scoring_performance():
    """Compare performance of different scoring strategies"""

    queries = [
        {
            "name": "Basic match",
            "body": {
                "query": {"match": {"description": "product"}}
            }
        },
        {
            "name": "Simple function_score",
            "body": {
                "query": {
                    "function_score": {
                        "query": {"match": {"description": "product"}},
                        "field_value_factor": {"field": "rating"}
                    }
                }
            }
        },
        {
            "name": "Multiple functions",
            "body": {
                "query": {
                    "function_score": {
                        "query": {"match": {"description": "product"}},
                        "functions": [
                            {"field_value_factor": {"field": "rating"}},
                            {"field_value_factor": {"field": "review_count"}},
                            {"filter": {"term": {"is_featured": True}}, "weight": 2}
                        ]
                    }
                }
            }
        },
        {
            "name": "Script scoring",
            "body": {
                "query": {
                    "function_score": {
                        "query": {"match": {"description": "product"}},
                        "script_score": {
                            "script": {
                                "source": "Math.log(2 + doc['rating'].value) * _score"
                            }
                        }
                    }
                }
            }
        }
    ]

    print("\nScoring Performance Comparison")
    print("-" * 60)
    print(f"{'Query Type':<25} {'Avg Time (ms)':<15} {'Results':<10}")
    print("-" * 60)

    for query_config in queries:
        times = []
        for _ in range(10):
            start = time.perf_counter()
            result = es.search(index="products", body=query_config["body"], size=10)
            times.append((time.perf_counter() - start) * 1000)

        avg_time = sum(times) / len(times)
        hit_count = result["hits"]["total"]["value"]

        print(f"{query_config['name']:<25} {avg_time:<15.2f} {hit_count:<10}")

compare_scoring_performance()
