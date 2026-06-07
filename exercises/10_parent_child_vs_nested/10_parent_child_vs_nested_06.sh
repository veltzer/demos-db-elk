#!/bin/bash -eu
curl -X GET "localhost:9200/blog_parent_child/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "has_child": {
      "type": "comment",
      "query": {
        "match": { "comment_text": "helpful" }
      }
    }
  }
}'
