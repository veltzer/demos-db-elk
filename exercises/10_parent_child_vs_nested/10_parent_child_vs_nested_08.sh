#!/bin/bash
curl -X GET "localhost:9200/blog_parent_child/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "term": { "relation": "comment" } },
        { "term": { "commenter": "Alice" } }
      ]
    }
  }
}'
