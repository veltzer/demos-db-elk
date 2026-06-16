#!/usr/bin/env python

import time
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")


def measure_scroll_performance(index_name, query_body, scroll_size=1000):
    """Measure performance of scrolling through large result sets"""
    
    start_time = time.perf_counter()
    
    # Initialize scroll
    result = es.search(
        index=index_name,
        body={
            **query_body,
            "size": scroll_size
        },
        scroll='2m'
    )
    
    scroll_id = result['_scroll_id']
    total_hits = result['hits']['total']['value']
    retrieved = len(result['hits']['hits'])
    
    # Continue scrolling
    while retrieved < total_hits:
        result = es.scroll(scroll_id=scroll_id, scroll='2m')
        retrieved += len(result['hits']['hits'])
        
        if len(result['hits']['hits']) == 0:
            break
    
    # Clear scroll
    es.clear_scroll(scroll_id=scroll_id)
    
    end_time = time.perf_counter()
    total_time = (end_time - start_time) * 1000
    
    return {
        'total_hits': total_hits,
        'total_time_ms': total_time,
        'docs_per_second': (total_hits / total_time) * 1000 if total_time > 0 else 0
    }

print("\n" + "=" * 60)
print("SCROLL PERFORMANCE TEST")
print("=" * 60)

# Query that returns many results
large_result_query = {
    "query": {
        "range": {
            "age": {"gte": 20, "lte": 60}
        }
    }
}

print("\nScrolling through large result set:")
result = measure_scroll_performance('users_indexed', large_result_query)
print(f"  Total documents: {result['total_hits']}")
print(f"  Total time: {result['total_time_ms']:.2f}ms")
print(f"  Throughput: {result['docs_per_second']:.0f} docs/second")
