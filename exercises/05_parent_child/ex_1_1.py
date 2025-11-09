from elasticsearch import Elasticsearch
from datetime import datetime
import json

es = Elasticsearch(["http://localhost:9200"])

# Delete index if exists
if es.indices.exists(index="blog_system"):
    es.indices.delete(index="blog_system")

# Create index with parent-child relationship
mapping = {
    "mappings": {
        "properties": {
            "join_field": {
                "type": "join",
                "relations": {
                    "blog_post": ["comment", "author_note"],  # blog_post can have comments and author_notes
                    "comment": "reply"  # comments can have replies
                }
            },
            "title": {"type": "text"},
            "content": {"type": "text"},
            "author": {"type": "keyword"},
            "created_at": {"type": "date"},
            "tags": {"type": "keyword"},
            "views": {"type": "integer"},
            "likes": {"type": "integer"},
            "status": {"type": "keyword"}
        }
    }
}

es.indices.create(index="blog_system", body=mapping)
print("Index created with parent-child relationship")
