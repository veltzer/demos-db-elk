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
