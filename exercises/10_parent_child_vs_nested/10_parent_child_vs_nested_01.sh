#!/bin/bash
curl -X PUT "localhost:9200/blog_nested?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "title": { "type": "text" },
      "author": { "type": "keyword" },
      "comments": {
        "type": "nested",
        "properties": {
          "text": { "type": "text" },
          "commenter": { "type": "keyword" },
          "date": { "type": "date" }
        }
      }
    }
  }
}'
