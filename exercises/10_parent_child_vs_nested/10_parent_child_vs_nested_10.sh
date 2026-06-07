#!/bin/bash
curl -X POST "localhost:9200/blog_parent_child/_doc/103?routing=1&pretty" -H 'Content-Type: application/json' -d'
{
  "comment_text": "I bookmarked this post!",
  "commenter": "Charlie",
  "date": "2024-01-17",
  "relation": { "name": "comment", "parent": "1" }
}'
