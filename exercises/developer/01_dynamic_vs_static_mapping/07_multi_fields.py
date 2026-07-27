#!/usr/bin/env python
"""
Query a multi-field mapping through both its text and its keyword sub-field
"""

from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Delete index if it exists
if es.indices.exists(index="dynamic_test"):
    es.indices.delete(index="dynamic_test")

# Search using the main text field
print(es.search(
    index="static_test",
    body={
        "query": {
            "match": {
                "name": "alice"  # Case-insensitive, analyzed
            }
        }
    }
))

# Search using the keyword sub-field
print(es.search(
    index="static_test",
    body={
        "query": {
            "term": {
                "name.keyword": "Alice Johnson"  # Exact match required
            }
        }
    }
))
