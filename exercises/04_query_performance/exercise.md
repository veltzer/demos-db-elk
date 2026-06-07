# Query Performance and Indexing in Elasticsearch

## Objective

Learn how to measure Elasticsearch query performance and understand the impact
of field indexing on query speed.

## Prerequisites

- Python 3.x with modules: `elasticsearch`, `faker`
- Elasticsearch running on <http://localhost:9200>
- Install required modules:

```bash
pip install elasticsearch faker
```

## Part 1: Generate Test Data

First, create test data using the provided script:

See [`04_query_performance_01.sh`](./04_query_performance_01.sh)

This creates two indices:

- `users_indexed`: All fields are indexed (searchable)
- `users_non_indexed`: Some fields have `index: false` (stored but not searchable)

## Part 2: Query Performance Measurement

### Exercise 2.1: Basic Query Timing

See [`04_query_performance_01.py`](./04_query_performance_01.py)

### Exercise 2.2: Compare Indexed vs Non-Indexed Fields

See [`04_query_performance_02.py`](./04_query_performance_02.py)

### Exercise 2.3: Using Elasticsearch's Profile API

See [`04_query_performance_03.py`](./04_query_performance_03.py)

### Exercise 2.4: Aggregation Performance

See [`04_query_performance_04.py`](./04_query_performance_04.py)

### Exercise 2.5: Scroll Performance for Large Result Sets

See [`04_query_performance_05.py`](./04_query_performance_05.py)

## Part 3: Advanced Performance Testing

### Exercise 3.1: Concurrent Query Performance

See [`04_query_performance_06.py`](./04_query_performance_06.py)

### Exercise 3.2: Script to Demonstrate Non-Indexed Field Impact

See [`04_query_performance_07.py`](./04_query_performance_07.py)

## Part 4: Best Practices and Optimization

### Exercise 4.1: Identify Fields to Not Index

See [`04_query_performance_08.py`](./04_query_performance_08.py)

## Summary and Key Takeaways

1. **Non-indexed fields cannot be searched** - Queries will fail with an error
1. **Non-indexed fields can still be retrieved** - They appear in search results
1. **Performance impact** - Indexed fields enable fast searches; without
   indexing, fields cannot be queried at all
1. **Use cases for `index: false`**:
   - Display-only fields
   - Large text fields not used for search
   - Binary/encoded data
   - Internal tracking fields

1. **Best practices**:
   - Analyze field usage before deciding on indexing
   - Use `index: false` for fields that are never searched
   - Consider storage vs query requirements
   - Monitor index size and performance

## Challenge Exercises

1. **Create a hybrid mapping** where commonly searched fields are indexed and
   rarely used fields are not
1. **Measure index size difference** between fully indexed and partially indexed
   indices
1. **Test update performance** when updating indexed vs non-indexed fields
1. **Design a mapping strategy** for a real-world application optimizing for both
   storage and query performance
