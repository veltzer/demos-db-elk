#!/bin/bash -eu
curl -X PUT "localhost:9200/blog_parent_child?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "title": { "type": "text" },
      "author": { "type": "keyword" },
      "comment_text": { "type": "text" },
      "commenter": { "type": "keyword" },
      "date": { "type": "date" },
      "relation": {
        "type": "join",
        "relations": { "post": "comment" }
      }
    }
  }
}'
