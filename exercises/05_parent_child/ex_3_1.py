#!/bin/env python

from elasticsearch import Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Get blog posts with their comments included
inner_hits_query = {
    "query": {
        "has_child": {
            "type": "comment",
            "query": {"match_all": {}},
            "inner_hits": {
                "size": 3,
                "sort": [{"likes": {"order": "desc"}}]
            }
        }
    }
}

result = es.search(index="blog_system", body=inner_hits_query)
print("Blog posts with their top comments:")
for hit in result["hits"]["hits"]:
    print(f"\nPost: {hit['_source']['title']}")
    if "inner_hits" in hit:
        print("  Top comments:")
        for comment in hit["inner_hits"]["comment"]["hits"]["hits"]:
            print(f"    - {comment['_source']['author']}: {comment['_source']['content'][:40]}...")
