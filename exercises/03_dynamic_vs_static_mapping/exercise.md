# Dynamic vs Static Mappings in Elasticsearch

## Objective

Learn the differences between dynamic and static mappings in Elasticsearch
and understand when to use each approach.

## Prerequisites

- Python 3.x installed
- Elasticsearch running locally (default: <http://localhost:9200>)
- Python elasticsearch module installed (`pip install elasticsearch`)

## Background

### Dynamic Mapping

- Elasticsearch automatically detects and adds new fields when documents are indexed
- Field types are inferred from the data
- Convenient but can lead to mapping conflicts

### Static Mapping

- You explicitly define the mapping before indexing data
- Provides control over field types and indexing options
- Prevents mapping conflicts and ensures data consistency

## Part 1: Dynamic Mapping

### Exercise 1.1: Observe Dynamic Mapping Behavior

See [`script_1_1.py`](./script_1_1.py)

**Task:** Run the code and observe the field types Elasticsearch assigned automatically.

### Exercise 1.2: Dynamic Mapping Conflicts

See [`script_1_2.py`](./script_1_2.py)

**Task:** Run this code and observe the mapping conflict error. Why does it occur?

## Part 2: Static Mapping

### Exercise 2.1: Create Static Mapping

See [`script_2_1.py`](./script_2_1.py)

**Task:** Create the index with static mapping and compare it to the dynamic
mapping from Part 1.

### Exercise 2.2: Index Documents with Static Mapping

See [`script_2_2.py`](./script_2_2.py)

**Task:** Index the documents and verify they were indexed successfully.

## Part 3: Comparing Search Capabilities

### Exercise 3.1: Text vs Keyword Fields

See [`script_3_1.py`](./script_3_1.py)

**Task:** Run both searches and observe the difference between text and keyword
field searches.

### Exercise 3.2: Aggregations

See [`script_3_2.py`](./script_3_2.py)

**Task:** Run the aggregation and analyze the results.

## Part 4: Advanced Mapping Features

### Exercise 4.1: Multi-fields

See [`script_4_1.py`](./script_4_1.py)

**Task:** Compare the results of searching on `name` vs `name.keyword`.

### Exercise 4.2: Disable Dynamic Mapping

See [`script_4_2.py`](./script_4_2.py)

**Task:** Observe what happens when trying to index a document with unmapped
fields when dynamic mapping is set to "strict".

## Challenges

### Challenge 1: Design a Mapping

Design and implement a static mapping for an e-commerce product catalog with
the following requirements:

- Product name (searchable and sortable)
- Description (full-text searchable)
- Price (numeric, for range queries)
- Categories (multiple values, for filtering)
- In stock (boolean)
- Created date
- Rating (1-5 scale)

### Challenge 2: Migration Strategy

Write a Python script that:

1. Reads the mapping from an existing index
1. Creates a new index with modified mapping
1. Reindexes all documents from the old index to the new one
1. Verifies the migration was successful

### Challenge 3: Dynamic Templates

Research and implement dynamic templates to automatically map fields based on
naming patterns:

- Fields ending with `_date` should be mapped as dates
- Fields starting with `is_` should be mapped as booleans
- Fields ending with `_count` should be mapped as integers

## Best Practices

1. **Always define mappings explicitly for production systems**
1. **Use multi-fields when you need both analyzed and exact matching**
1. **Set `dynamic: false` or `dynamic: strict` to prevent mapping explosions**
1. **Test your mappings with sample data before going to production**
1. **Document your mapping decisions and field purposes**
1. **Consider using index templates for consistent mappings across indices**

## Summary Questions

1. What are the main differences between dynamic and static mappings?
1. When would you choose dynamic mapping over static mapping?
1. What is the purpose of multi-fields in Elasticsearch?
1. How can you prevent mapping conflicts in production?
1. What are the implications of changing a fields mapping after data has been
   indexed?

## Resources

- [Elasticsearch Mapping Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html)
- [Dynamic Mapping](https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic-mapping.html)
- [Field Data Types](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html)
- [Python Elasticsearch Client](https://elasticsearch-py.readthedocs.io/)
