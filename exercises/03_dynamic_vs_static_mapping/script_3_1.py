#!/usr/bin/env python

from elasticsearch import Elasticsearch
from datetime import datetime

# Connect to Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Delete index if it exists
if es.indices.exists(index="dynamic_test"):
    es.indices.delete(index="dynamic_test")

# Search on text field (analyzed)
text_search = es.search(
    index="static_test",
    body={
        "query": {
            "match": {
                "description": "python developer"
            }
        }
    }
)

print("Text field search results:")
for hit in text_search["hits"]["hits"]:
    print(f"- {hit["_source"]["name"]}: {hit["_source"]["description"]}")

# Search on keyword field (exact match)
keyword_search = es.search(
    index="static_test",
    body={
        "query": {
            "term": {
                "tags": "python"
            }
        }
    }
)

print("\nKeyword field search results:")
for hit in keyword_search["hits"]["hits"]:
    print(f"- {hit["_source"]["name"]}: {hit["_source"]["tags"]}")
