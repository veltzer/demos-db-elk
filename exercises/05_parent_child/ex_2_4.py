#!/bin/env python

from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Get blog posts with comment count
children_agg_query = {
    "query": {
        "term": {"join_field": "blog_post"}
    },
    "aggs": {
        "comment_count": {
            "children": {
                "type": "comment"
            },
            "aggs": {
                "top_commenters": {
                    "terms": {
                        "field": "author",
                        "size": 5
                    }
                }
            }
        }
    }
}

result = es.search(index="blog_system", body=children_agg_query)
print("Top commenters across all blog posts:")
if "comment_count" in result["aggregations"]:
    for bucket in result["aggregations"]["comment_count"]["top_commenters"]["buckets"]:
        print(f"- {bucket['key']}: {bucket['doc_count']} comments")
