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
