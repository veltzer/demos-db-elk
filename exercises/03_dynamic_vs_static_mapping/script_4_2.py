#!/usr/bin/env python

from elasticsearch import Elasticsearch
from datetime import datetime

# Connect to Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Delete index if it exists
if es.indices.exists(index="dynamic_test"):
    es.indices.delete(index="dynamic_test")

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
