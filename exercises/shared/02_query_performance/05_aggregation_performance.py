#!/usr/bin/env python
"""
Measure the cost of aggregation queries
"""

import time

from elastic_transport import TransportError
from elasticsearch import ApiError, Elasticsearch

es = Elasticsearch("http://localhost:9200")


def measure_aggregation_performance(index_name, agg_body):
    """Measure aggregation query performance"""

    start = time.perf_counter()
    result = es.search(index=index_name, body=agg_body)
    end = time.perf_counter()

    elapsed_ms = (end - start) * 1000
    es_took = result.get('took', 0)

    return {
        'client_time_ms': elapsed_ms,
        'es_took_ms': es_took,
        'bucket_count': len(result['aggregations'].get('agg_result', {}).get('buckets', []))
    }

# Test aggregation on indexed vs non-indexed field
agg_query_indexed_field = {
    "size": 0,
    "aggs": {
        "agg_result": {
            "terms": {
                "field": "department",
                "size": 20
            }
        }
    }
}

print("\n" + "=" * 60)
print("AGGREGATION PERFORMANCE TEST")
print("=" * 60)

print("\nAggregation on indexed field (department):")
summary = measure_aggregation_performance('users_indexed', agg_query_indexed_field)
print(f"  ES took: {summary['es_took_ms']}ms")
print(f"  Client time: {summary['client_time_ms']:.2f}ms")
print(f"  Buckets: {summary['bucket_count']}")

# Try aggregation on non-indexed field (will fail)
agg_query_non_indexed_field = {
    "size": 0,
    "aggs": {
        "agg_result": {
            "terms": {
                "field": "email",  # This is not indexed in users_non_indexed
                "size": 20
            }
        }
    }
}

print("Aggregation on non-indexed field (email) in users_non_indexed:")
try:
    summary = measure_aggregation_performance('users_non_indexed', agg_query_non_indexed_field)
    print(f"  ES took: {summary['es_took_ms']}ms")
except (ApiError, TransportError) as e:
    print("  Error: Cannot aggregate on non-indexed field!")
    print(f"  {str(e)[:150]}...")
