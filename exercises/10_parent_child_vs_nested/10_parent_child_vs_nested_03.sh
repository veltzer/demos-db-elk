#!/bin/bash -eu
curl -X POST "localhost:9200/blog_nested/_doc/1?pretty" -H 'Content-Type: application/json' -d'
{
  "title": "Getting Started with Elasticsearch",
  "author": "John",
  "comments": [
    {
      "text": "Great tutorial!",
      "commenter": "Alice",
      "date": "2024-01-15"
    },
    {
      "text": "Very helpful, thanks!",
      "commenter": "Bob",
      "date": "2024-01-16"
    }
  ]
}'
