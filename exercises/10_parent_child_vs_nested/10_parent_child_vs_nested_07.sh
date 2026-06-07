#!/bin/bash -eu
curl -X GET "localhost:9200/blog_nested/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "nested": {
      "path": "comments",
      "query": {
        "term": { "comments.commenter": "Alice" }
      },
      "inner_hits": {}
    }
  }
}'
