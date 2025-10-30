# Exercise: Query Performance and Indexing in Elasticsearch

## Objective
Learn how to measure Elasticsearch query performance and understand the impact of field indexing on query speed.

## Prerequisites
- Python 3.x with modules: `elasticsearch`, `faker`
- Elasticsearch running on http://localhost:9200
- Install required modules:

```bash
pip install elasticsearch faker
```

## Part 1: Generate Test Data

First, create test data using the provided script:

```bash
# Create both indexed and non-indexed indices with 10,000 documents each
python create_data.py --create-both --docs 10000

# Or create more documents for better performance testing
python create_data.py --create-both --docs 50000
```

This creates two indices:
- `users_indexed`: All fields are indexed (searchable)
- `users_non_indexed`: Some fields have `index: false` (stored but not searchable)

## Part 2: Query Performance Measurement

### Exercise 2.1: Basic Query Timing

```python
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
        
        # Also get Elasticsearchs internal took time
        es_took = result.get("took", 0)
        
        if i == 0:  # Print first result details
            print(f"  Hits: {result["hits"]["total"]["value"]}")
        
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
print(f"  Average: {result[\"avg_ms\"]:.2f}ms")
print(f"  Min: {result[\"min_ms\"]:.2f}ms, Max: {result[\"max_ms\"]:.2f}ms")
```

### Exercise 2.2: Compare Indexed vs Non-Indexed Fields

```python
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
        print(f"  Average: {indexed_result[\"avg_ms\"]:.2f}ms")
    except Exception as e:
        print(f"  Error: {e}")
        indexed_result = None
    
    # Test on non-indexed version
    try:
        print("\nusers_non_indexed (field NOT indexed):")
        non_indexed_result = measure_query_time(\"users_non_indexed\", query, runs=10)
        print(f"  Average: {non_indexed_result[\"avg_ms\"]:.2f}ms")
    except Exception as e:
        print(f"  Error: Cannot search on non-indexed field!")
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
```

### Exercise 2.3: Using Elasticsearch's Profile API

```python
def profile_query(index_name, query_body):
    """Use Elasticsearch's Profile API to get detailed timing"""
    
    profile_query = {
        **query_body,
        "profile": True
    }
    
    result = es.search(index=index_name, body=profile_query)
    
    print(f"\nProfile for index: {index_name}")
    print("-" * 50)
    print(f"Total took: {result['took']}ms")
    print(f"Total hits: {result['hits']['total']['value']}")
    
    if 'profile' in result:
        shards = result['profile']['shards']
        for i, shard in enumerate(shards):
            print(f"\nShard {i}:")
            for search in shard['searches']:
                print(f"  Query type: {search['query'][0]['type']}")
                print(f"  Time: {search['query'][0]['time_in_nanos'] / 1_000_000:.2f}ms")
                print(f"  Breakdown:")
                breakdown = search['query'][0]['breakdown']
                for key, value in sorted(breakdown.items(), key=lambda x: x[1], reverse=True)[:5]:
                    if value > 0:
                        print(f"    {key}: {value / 1_000_000:.2f}ms")

# Profile a complex query
complex_query = {
    "query": {
        "bool": {
            "must": [
                {"range": {"age": {"gte": 25, "lte": 50}}},
                {"term": {"is_active": True}}
            ],
            "should": [
                {"match": {"full_name": "John"}},
                {"terms": {"tags": ["python", "java"]}}
            ],
            "minimum_should_match": 1
        }
    }
}

profile_query('users_indexed', complex_query)
```

### Exercise 2.4: Aggregation Performance

```python
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
result = measure_aggregation_performance('users_indexed', agg_query_indexed_field)
print(f"  ES took: {result['es_took_ms']}ms")
print(f"  Client time: {result['client_time_ms']:.2f}ms")
print(f"  Buckets: {result['bucket_count']}")

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
    result = measure_aggregation_performance('users_non_indexed', agg_query_non_indexed_field)
    print(f"  ES took: {result['es_took_ms']}ms")
except Exception as e:
    print(f"  Error: Cannot aggregate on non-indexed field!")
    print(f"  {str(e)[:150]}...")
```

### Exercise 2.5: Scroll Performance for Large Result Sets

```python
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
```

## Part 3: Advanced Performance Testing

### Exercise 3.1: Concurrent Query Performance

```python
#!/usr/bin/env python

import concurrent.futures
import statistics

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
```

### Exercise 3.2: Script to Demonstrate Non-Indexed Field Impact

```python
def demonstrate_index_impact():
    """Complete demonstration of indexing impact on query performance"""
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION: Impact of Field Indexing on Query Performance")
    print("=" * 70)
    
    # List of test cases
    test_cases = [
        {
            'field': 'email',
            'value': 'test@example.com',
            'indexed_in_first': True,
            'indexed_in_second': False,
            'query_type': 'term'
        },
        {
            'field': 'salary',
            'value': {'gte': 50000, 'lte': 100000},
            'indexed_in_first': True,
            'indexed_in_second': False,
            'query_type': 'range'
        },
        {
            'field': 'bio',
            'value': 'developer',
            'indexed_in_first': True,
            'indexed_in_second': False,
            'query_type': 'match'
        }
    ]
    
    results = []
    
    for test in test_cases:
        print(f"\n{'-' * 60}")
        print(f"Testing field: {test['field']} (Query type: {test['query_type']})")
        print(f"  Indexed in users_indexed: {test['indexed_in_first']}")
        print(f"  Indexed in users_non_indexed: {test['indexed_in_second']}")
        print()
        
        if test['query_type'] == 'term':
            query = {"query": {"term": {test['field']: test['value']}}}
        elif test['query_type'] == 'range':
            query = {"query": {"range": {test['field']: test['value']}}}
        elif test['query_type'] == 'match':
            query = {"query": {"match": {test['field']: test['value']}}}
        
        # Test on indexed version
        if test['indexed_in_first']:
            try:
                result1 = measure_query_time('users_indexed', query, runs=5)
                print(f"  users_indexed: {result1['avg_ms']:.2f}ms (Success)")
                indexed_time = result1['avg_ms']
            except Exception as e:
                print(f"  users_indexed: Failed - {str(e)[:50]}")
                indexed_time = None
        
        # Test on non-indexed version
        if not test['indexed_in_second']:
            try:
                result2 = measure_query_time('users_non_indexed', query, runs=5)
                print(f"  users_non_indexed: {result2['avg_ms']:.2f}ms (Success)")
                non_indexed_time = result2['avg_ms']
            except Exception as e:
                print(f"  users_non_indexed: FAILED - Cannot search non-indexed field!")
                non_indexed_time = None
        
        results.append({
            'field': test['field'],
            'indexed_time': indexed_time,
            'non_indexed_time': non_indexed_time
        })
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: Query Performance Impact")
    print("=" * 70)
    print("\nKey Findings:")
    print("1. Non-indexed fields CANNOT be searched or used in queries")
    print("2. Queries on non-indexed fields will return an error")
    print("3. Non-indexed fields can still be retrieved in search results")
    print("4. Use 'index: false' for fields that only need to be stored, not searched")
    print("\nPerformance Results:")
    print(f"{'Field':<20} {'Indexed Query':<20} {'Non-Indexed Query':<20}")
    print("-" * 60)
    for r in results:
        indexed = f"{r['indexed_time']:.2f}ms" if r['indexed_time'] else "N/A"
        non_indexed = "Cannot Query" if r['non_indexed_time'] is None else f"{r['non_indexed_time']:.2f}ms"
        print(f"{r['field']:<20} {indexed:<20} {non_indexed:<20}")

# Run the demonstration
demonstrate_index_impact()
```

## Part 4: Best Practices and Optimization

### Exercise 4.1: Identify Fields to Not Index

```python
def analyze_field_usage():
    """Analyze which fields might benefit from having indexing disabled"""
    
    print("\n" + "=" * 60)
    print("FIELD INDEXING RECOMMENDATIONS")
    print("=" * 60)
    
    recommendations = {
        'Should remain indexed': [
            'user_id - Used for lookups',
            'username - Searched frequently',
            'department - Used in filters and aggregations',
            'tags - Used in term queries',
            'is_active - Used in boolean filters',
            'age - Used in range queries',
            'joined_date - Used in date range queries'
        ],
        'Consider disabling index': [
            'metadata - Large text field only for display',
            'bio - If only displayed, not searched',
            'location.latitude/longitude - If not used for geo queries',
            'post_count - If only displayed in results',
            'followers - If only displayed in results'
        ],
        'Definitely disable index': [
            'Internal IDs not used for search',
            'Binary or base64 encoded data',
            'Large text fields only for storage',
            'Computed fields that are never queried'
        ]
    }
    
    for category, fields in recommendations.items():
        print(f"\n{category}:")
        for field in fields:
            print(f"  - {field}")
    
    print("\n" + "-" * 60)
    print("Memory and Performance Benefits of Disabling Indexing:")
    print("  1. Reduced index size (can be 30-50% smaller)")
    print("  2. Faster indexing speed for new documents")
    print("  3. Lower memory usage")
    print("  4. Faster cluster state updates")
    print("  5. Reduced disk I/O")

analyze_field_usage()
```

## Summary and Key Takeaways

1. **Non-indexed fields cannot be searched** - Queries will fail with an error
2. **Non-indexed fields can still be retrieved** - They appear in search results
3. **Performance impact** - Indexed fields enable fast searches; without indexing, fields cannot be queried at all
4. **Use cases for `index: false`**:
   - Display-only fields
   - Large text fields not used for search
   - Binary/encoded data
   - Internal tracking fields

5. **Best practices**:
   - Analyze field usage before deciding on indexing
   - Use `index: false` for fields that are never searched
   - Consider storage vs query requirements
   - Monitor index size and performance

## Challenge Exercises

1. **Create a hybrid mapping** where commonly searched fields are indexed and rarely used fields are not
2. **Measure index size difference** between fully indexed and partially indexed indices
3. **Test update performance** when updating indexed vs non-indexed fields
4. **Design a mapping strategy** for a real-world application optimizing for both storage and query performance
