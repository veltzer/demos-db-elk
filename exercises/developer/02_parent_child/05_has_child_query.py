#!/usr/bin/env python
"""
Find parent blog posts by the properties of their child comments with has_child
"""
from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Find blog posts that have comments from a specific user
has_child_query = {
    "query": {
        "has_child": {
            "type": "comment",
            "query": {
                "term": {
                    "author": "user_jane"
                }
            }
        }
    }
}

result = es.search(index="blog_system", body=has_child_query)
print("Blog posts with comments from user_jane:")
for hit in result["hits"]["hits"]:
    f = hit["_source"]["title"]
    print(f"- {f}")
