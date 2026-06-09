#!/usr/bin/env python

import time
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

def measure_query_time(index_name, query_body, runs=5):
    """Measure query execution time over multiple runs"""
    times = []
    
    for i in range(runs):
        start = time.perf_counter()
        result = es.search(index=index_name, body=query_body)
        end = time.perf_counter()
        
        elapsed_ms = (end - start) * 1000
        times.append(elapsed_ms)
        
        if i == 0:  # Print first result details
            print(f"  Hits: {result['hits']['total']['value']}")
        
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    return {
        "avg_ms": avg_time,
        "min_ms": min_time,
        "max_ms": max_time,
        "times": times
    }

# Test 1: Search on indexed field
print("Test 1: Searching indexed field (department)")
print("-" * 50)

query_indexed = {
    "query": {
        "term": {
            "department": "Engineering"
        }
    }
}

print("Index: users_indexed")
result = measure_query_time("users_indexed", query_indexed)
print(f"  Average: {result['avg_ms']:.2f}ms")
print(f"  Min: {result['min_ms']:.2f}ms, Max: {result['max_ms']:.2f}ms")
