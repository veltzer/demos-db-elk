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


def compare_field_performance(field_name, search_value, query_type="term"):
    """Compare query performance between indexed and non-indexed versions"""

    if query_type == "term":
        query = {
            "query": {
                "term": {
                    field_name: search_value
                }
            }
        }
    elif query_type == "range":
        query = {
            "query": {
                "range": {
                    field_name: search_value
                }
            }
        }
    elif query_type == "match":
        query = {
            "query": {
                "match": {
                    field_name: search_value
                }
            }
        }

    print(f"\nComparing field: {field_name}")
    print(f"Query type: {query_type}")
    print("=" * 60)

    # Test on indexed version
    try:
        print("users_indexed (field IS indexed):")
        indexed_result = measure_query_time("users_indexed", query, runs=10)
        print(f"  Average: {indexed_result['avg_ms']:.2f}ms")
    except Exception as e:
        print(f"  Error: {e}")
        indexed_result = None

    # Test on non-indexed version
    try:
        print("\nusers_non_indexed (field NOT indexed):")
        non_indexed_result = measure_query_time("users_non_indexed", query, runs=10)
        print(f"  Average: {non_indexed_result['avg_ms']:.2f}ms")
    except Exception as e:
        print("  Error: Cannot search on non-indexed field!")
        print(f"  {str(e)[:100]}...")
        non_indexed_result = None

    return indexed_result, non_indexed_result


# Test various fields
print("\n" + "=" * 60)
print("PERFORMANCE COMPARISON: Indexed vs Non-Indexed Fields")
print("=" * 60)

# Field that's indexed in both
compare_field_performance('username', 'john_smith', 'term')

# Field that's NOT indexed in users_non_indexed
compare_field_performance('email', 'user@example.com', 'term')

# Numeric field comparison
compare_field_performance('salary', {'gte': 50000, 'lte': 100000}, 'range')

# Text field comparison
compare_field_performance('bio', 'software engineer', 'match')
