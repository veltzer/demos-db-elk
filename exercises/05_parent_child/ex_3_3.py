#!/bin/env python

from elasticsearch import Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Find blog posts that have comments with replies
multi_level_query = {
    "query": {
        "has_child": {
            "type": "comment",
            "query": {
                "has_child": {
                    "type": "reply",
                    "query": {"match_all": {}}
                }
            }
        }
    }
}

result = es.search(index="blog_system", body=multi_level_query)
print("Blog posts with comments that have replies:")
for hit in result["hits"]["hits"]:
    print(f"- {hit['_source']['title']}")
