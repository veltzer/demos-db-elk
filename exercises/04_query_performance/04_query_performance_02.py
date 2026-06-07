#!/usr/bin/env python
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
