# Exercise: Dynamic vs Static Mappings in Elasticsearch

## Objective
Learn the differences between dynamic and static mappings in Elasticsearch and understand when to use each approach.

## Prerequisites
- Python 3.x installed
- Elasticsearch running locally (default: http://localhost:9200)
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

```python
#!/usr/bin/env python

from elasticsearch import Elasticsearch
from datetime import datetime

# Connect to Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Delete index if it exists
if es.indices.exists(index="dynamic_test"):
    es.indices.delete(index="dynamic_test")

# Index a document without defining mapping
doc1 = {
    "name": "John Doe",
    "age": 30,
    "joined_date": "2024-01-15",
    "is_active": True,
    "score": 95.5
}

es.index(index="dynamic_test", id=1, body=doc1)

# Check the dynamically created mapping
mapping = es.indices.get_mapping(index="dynamic_test")
print("Dynamic Mapping Created:")
print(mapping)
```

**Task:** Run the code and observe the field types Elasticsearch assigned automatically.

### Exercise 1.2: Dynamic Mapping Conflicts

```python
#!/usr/bin/env python

# Try to index a document with conflicting field type
doc2 = {
    "name": "Jane Smith",
    "age": "thirty",  # This will cause an error - age was mapped as long
    "joined_date": "2024-02-20",
    "is_active": True,
    "score": 88.0
}

try:
    es.index(index="dynamic_test", id=2, body=doc2)
except Exception as e:
    print(f"Error: {e}")
```

**Task:** Run this code and observe the mapping conflict error. Why does it occur?

## Part 2: Static Mapping

### Exercise 2.1: Create Static Mapping

```python
#!/usr/bin/env python

from elasticsearch import Elasticsearch
from datetime import datetime

# Connect to Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Delete index if it exists
if es.indices.exists(index="static_test"):
    es.indices.delete(index="static_test")

# Define explicit mapping
mapping = {
    "mappings": {
        "properties": {
            "name": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword"
                    }
                }
            },
            "age": {
                "type": "integer"
            },
            "joined_date": {
                "type": "date",
                "format": "yyyy-MM-dd"
            },
            "is_active": {
                "type": "boolean"
            },
            "score": {
                "type": "float"
            },
            "description": {
                "type": "text",
                "analyzer": "standard"
            },
            "tags": {
                "type": "keyword"
            }
        }
    }
}

# Create index with static mapping
es.indices.create(index="static_test", body=mapping)

# Verify the mapping
created_mapping = es.indices.get_mapping(index="static_test")
print("Static Mapping Created:")
print(created_mapping)
```

**Task:** Create the index with static mapping and compare it to the dynamic mapping from Part 1.

### Exercise 2.2: Index Documents with Static Mapping

```python
#!/usr/bin/env python

from elasticsearch import Elasticsearch
from datetime import datetime

# Connect to Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Delete index if it exists
if es.indices.exists(index="dynamic_test"):
    es.indices.delete(index="dynamic_test")

# Index multiple documents
documents = [
    {
        "name": "Alice Johnson",
        "age": 28,
        "joined_date": "2024-01-10",
        "is_active": True,
        "score": 92.3,
        "description": "Senior developer with expertise in Python and Java",
        "tags": ["python", "java", "backend"]
    },
    {
        "name": "Bob Wilson",
        "age": 35,
        "joined_date": "2024-02-15",
        "is_active": False,
        "score": 87.5,
        "description": "DevOps engineer specializing in cloud infrastructure",
        "tags": ["aws", "docker", "kubernetes"]
    },
    {
        "name": "Carol Martinez",
        "age": 31,
        "joined_date": "2024-03-01",
        "is_active": True,
        "score": 94.8,
        "description": "Full stack developer with React and Node.js experience",
        "tags": ["react", "nodejs", "fullstack"]
    }
]

for i, doc in enumerate(documents, 1):
    es.index(index="static_test", id=i, body=doc)

print(f"Indexed {len(documents)} documents")
```

**Task:** Index the documents and verify they were indexed successfully.

## Part 3: Comparing Search Capabilities

### Exercise 3.1: Text vs Keyword Fields

```python
#!/usr/bin/env python

from elasticsearch import Elasticsearch
from datetime import datetime

# Connect to Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Delete index if it exists
if es.indices.exists(index="dynamic_test"):
    es.indices.delete(index="dynamic_test")

# Search on text field (analyzed)
text_search = es.search(
    index="static_test",
    body={
        "query": {
            "match": {
                "description": "python developer"
            }
        }
    }
)

print("Text field search results:")
for hit in text_search["hits"]["hits"]:
    print(f"- {hit["_source"]["name"]}: {hit["_source"]["description"]}")

# Search on keyword field (exact match)
keyword_search = es.search(
    index="static_test",
    body={
        "query": {
            "term": {
                "tags": "python"
            }
        }
    }
)

print("\nKeyword field search results:")
for hit in keyword_search["hits"]["hits"]:
    print(f"- {hit["_source"]["name"]}: {hit["_source"]["tags"]}")
```

**Task:** Run both searches and observe the difference between text and keyword field searches.

### Exercise 3.2: Aggregations

```python
# Aggregation on keyword field
agg_result = es.search(
    index="static_test",
    body={
        "size": 0,
        "aggs": {
            "popular_tags": {
                "terms": {
                    "field": "tags",
                    "size": 10
                }
            },
            "avg_score": {
                "avg": {
                    "field": "score"
                }
            },
            "active_count": {
                "value_count": {
                    "field": "is_active"
                }
            }
        }
    }
)

print("Aggregation Results:")
print(f"Popular tags: {agg_result["aggregations"]["popular_tags"]["buckets"]}")
print(f"Average score: {agg_result["aggregations"]["avg_score"]["value"]}")
print(f"Active users count: {agg_result["aggregations"]["active_count"]["value"]}")
```

**Task:** Run the aggregation and analyze the results.

## Part 4: Advanced Mapping Features

### Exercise 4.1: Multi-fields

```python
# Search using the main text field
es.search(
    index="static_test",
    body={
        "query": {
            "match": {
                "name": "alice"  # Case-insensitive, analyzed
            }
        }
    }
)

# Search using the keyword sub-field
es.search(
    index="static_test",
    body={
        "query": {
            "term": {
                "name.keyword": "Alice Johnson"  # Exact match required
            }
        }
    }
)
```

**Task:** Compare the results of searching on `name` vs `name.keyword`.

### Exercise 4.2: Disable Dynamic Mapping

```python
# Create index with dynamic mapping disabled
strict_mapping = {
    "mappings": {
        "dynamic": "strict",  # Reject documents with unmapped fields
        "properties": {
            "title": {"type": "text"},
            "price": {"type": "float"}
        }
    }
}

if es.indices.exists(index="strict_test"):
    es.indices.delete(index="strict_test")

es.indices.create(index="strict_test", body=strict_mapping)

# Try to index document with unmapped field
try:
    es.index(
        index="strict_test",
        body={
            "title": "Product A",
            "price": 29.99,
            "category": "Electronics"  # This field is not mapped
        }
    )
except Exception as e:
    print(f"Error with strict mapping: {e}")
```

**Task:** Observe what happens when trying to index a document with unmapped fields when dynamic mapping is set to "strict".

## Challenges

### Challenge 1: Design a Mapping
Design and implement a static mapping for an e-commerce product catalog with the following requirements:
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
2. Creates a new index with modified mapping
3. Reindexes all documents from the old index to the new one
4. Verifies the migration was successful

### Challenge 3: Dynamic Templates
Research and implement dynamic templates to automatically map fields based on naming patterns:
- Fields ending with `_date` should be mapped as dates
- Fields starting with `is_` should be mapped as booleans
- Fields ending with `_count` should be mapped as integers

## Best Practices

1. **Always define mappings explicitly for production systems**
2. **Use multi-fields when you need both analyzed and exact matching**
3. **Set `dynamic: false` or `dynamic: strict` to prevent mapping explosions**
4. **Test your mappings with sample data before going to production**
5. **Document your mapping decisions and field purposes**
6. **Consider using index templates for consistent mappings across indices**

## Summary Questions

1. What are the main differences between dynamic and static mappings?
2. When would you choose dynamic mapping over static mapping?
3. What is the purpose of multi-fields in Elasticsearch?
4. How can you prevent mapping conflicts in production?
5. What are the implications of changing a fields mapping after data has been indexed?

## Resources

- [Elasticsearch Mapping Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html)
- [Dynamic Mapping](https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic-mapping.html)
- [Field Data Types](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html)
- [Python Elasticsearch Client](https://elasticsearch-py.readthedocs.io/)
