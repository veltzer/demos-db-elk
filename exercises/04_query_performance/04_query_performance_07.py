#!/usr/bin/env python
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
