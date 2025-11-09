#!/bin/env python

from elasticsearch import Elasticsearch
import time

es = Elasticsearch(["http://localhost:9200"])

def measure_parent_child_performance():
    """Measure query performance for parent-child relationships"""

    # Warm up
    es.search(index="blog_system", body={"query": {"match_all": {}}})

    queries = [
        {
            "name": "Simple parent query",
            "body": {"query": {"term": {"join_field": "blog_post"}}}
        },
        {
            "name": "Has child query",
            "body": {"query": {"has_child": {"type": "comment", "query": {"match_all": {}}}}}
        },
        {
            "name": "Has parent query",
            "body": {"query": {"has_parent": {"parent_type": "blog_post", "query": {"match_all": {}}}}}
        },
        {
            "name": "Parent-child with aggregation",
            "body": {
                "query": {"term": {"join_field": "blog_post"}},
                "aggs": {"comments": {"children": {"type": "comment"}}}
            }
        }
    ]

    print("\nParent-Child Query Performance:")
    print("-" * 50)

    for query in queries:
        times = []
        for _ in range(10):
            start = time.perf_counter()
            es.search(index="blog_system", body=query["body"])
            times.append((time.perf_counter() - start) * 1000)

        avg_time = sum(times) / len(times)
        print(f"{query['name']}: {avg_time:.2f}ms")

measure_parent_child_performance()
