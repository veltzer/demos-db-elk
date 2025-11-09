#!/bin/env python

from elasticsearch import Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Score blog posts based on comment activity
scoring_query = {
    "query": {
        "has_child": {
            "type": "comment",
            "score_mode": "sum",  # sum, avg, min, max, none
            "query": {
                "function_score": {
                    "query": {"match_all": {}},
                    "field_value_factor": {
                        "field": "likes",
                        "factor": 1.5,
                        "modifier": "log1p"
                    }
                }
            }
        }
    }
}

result = es.search(index="blog_system", body=scoring_query)
print("Blog posts scored by comment engagement:")
for hit in result["hits"]["hits"]:
    print(f"- {hit['_source']['title']} (score: {hit['_score']:.2f})")
