#!/usr/bin/env python

import concurrent.futures
import statistics
import time

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")


def run_concurrent_queries(index_name, query_body, num_threads=10, queries_per_thread=10):
    """Test query performance under concurrent load"""
    
    def run_queries():
        times = []
        for _ in range(queries_per_thread):
            start = time.perf_counter()
            es.search(index=index_name, body=query_body)
            end = time.perf_counter()
            times.append((end - start) * 1000)
        return times
    
    print(f"\nRunning {num_threads} concurrent threads, {queries_per_thread} queries each...")
    
    all_times = []
    start_time = time.perf_counter()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(run_queries) for _ in range(num_threads)]
        for future in concurrent.futures.as_completed(futures):
            all_times.extend(future.result())
    
    end_time = time.perf_counter()
    total_time = (end_time - start_time) * 1000
    
    return {
        'total_queries': len(all_times),
        'total_time_ms': total_time,
        'avg_query_time_ms': statistics.mean(all_times),
        'median_query_time_ms': statistics.median(all_times),
        'p95_query_time_ms': statistics.quantiles(all_times, n=20)[18],  # 95th percentile
        'queries_per_second': (len(all_times) / total_time) * 1000
    }

print("\n" + "=" * 60)
print("CONCURRENT QUERY PERFORMANCE TEST")
print("=" * 60)

simple_query = {
    "query": {
        "term": {
            "department": "Engineering"
        }
    }
}

result = run_concurrent_queries('users_indexed', simple_query, num_threads=10, queries_per_thread=20)
print(f"  Total queries: {result['total_queries']}")
print(f"  Total time: {result['total_time_ms']:.2f}ms")
print(f"  Average query time: {result['avg_query_time_ms']:.2f}ms")
print(f"  Median query time: {result['median_query_time_ms']:.2f}ms")
print(f"  95th percentile: {result['p95_query_time_ms']:.2f}ms")
print(f"  Throughput: {result['queries_per_second']:.0f} queries/second")
