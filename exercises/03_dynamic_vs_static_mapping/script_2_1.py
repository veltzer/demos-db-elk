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
