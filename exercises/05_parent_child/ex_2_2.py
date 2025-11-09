#!/bin/env python

from elasticsearch import Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Find comments for blog posts with specific tags
has_parent_query = {
    "query": {
        "has_parent": {
            "parent_type": "blog_post",
            "query": {
                "term": {
                    "tags": "tutorial"
                }
            }
        }
    }
}

result = es.search(index="blog_system", body=has_parent_query)
print("Comments on tutorial posts:")
for hit in result["hits"]["hits"]:
    print(f"- {hit['_source']['content'][:50]}... by {hit['_source']['author']}")
