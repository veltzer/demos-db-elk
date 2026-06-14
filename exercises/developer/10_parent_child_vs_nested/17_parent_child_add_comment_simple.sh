#!/bin/bash -eu
curl -X POST "localhost:9200/blog_parent_child/_doc/104?routing=1&pretty" -H 'Content-Type: application/json' -d'
{
  "comment_text": "Fourth comment!",
  "commenter": "David",
  "date": "2024-01-18",
  "relation": { "name": "comment", "parent": "1" }
}'

# Much simpler - just add new documents independently!
