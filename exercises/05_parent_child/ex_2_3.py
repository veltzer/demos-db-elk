#!/bin/env python

from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Get all children of a specific parent
parent_id_query = {
    "query": {
        "parent_id": {
            "type": "comment",
            "id": "post_1"
        }
    }
}

result = es.search(index="blog_system", body=parent_id_query)
print(f"Comments on post_1: {result['hits']['total']['value']}")
for hit in result["hits"]["hits"]:
    print(f"- {hit['_source']['author']}: {hit['_source']['content'][:50]}...")
