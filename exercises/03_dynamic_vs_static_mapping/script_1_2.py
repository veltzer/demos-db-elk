#!/usr/bin/env python

from elasticsearch import Elasticsearch
from datetime import datetime

# Connect to Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

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
