#!/bin/bash -eu
curl -X POST "localhost:9200/blog_parent_child/_doc/101?routing=1&pretty" -H 'Content-Type: application/json' -d'
{
  "comment_text": "Great tutorial! Updated my comment.",
  "commenter": "Alice",
  "date": "2024-01-15",
  "relation": { "name": "comment", "parent": "1" }
}'
