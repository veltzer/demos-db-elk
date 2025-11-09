#!/bin/env python

from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Alternative: Denormalized structure for comparison
if es.indices.exists(index="blog_denormalized"):
    es.indices.delete(index="blog_denormalized")

denormalized_mapping = {
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "content": {"type": "text"},
            "author": {"type": "keyword"},
            "comments": {
                "type": "nested",
                "properties": {
                    "content": {"type": "text"},
                    "author": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "likes": {"type": "integer"}
                }
            }
        }
    }
}

es.indices.create(index="blog_denormalized", body=denormalized_mapping)

# Index denormalized document
denormalized_doc = {
    "title": "Getting Started with Elasticsearch",
    "content": "Elasticsearch is a powerful search engine...",
    "author": "alice_tech",
    "comments": [
        {
            "content": "Great tutorial! This helped me understand the basics.",
            "author": "user_john",
            "created_at": "2024-01-15T12:30:00",
            "likes": 5
        },
        {
            "content": "Could you add more examples about aggregations?",
            "author": "user_jane",
            "created_at": "2024-01-15T15:45:00",
            "likes": 3
        }
    ]
}

es.index(index="blog_denormalized", id="post_1", body=denormalized_doc)
print("\nCreated denormalized structure for comparison")
