#!/bin/bash
# Parent document
curl -X POST "localhost:9200/blog_parent_child/_doc/1?pretty" -H 'Content-Type: application/json' -d'
{
  "title": "Getting Started with Elasticsearch",
  "author": "John",
  "relation": { "name": "post" }
}'

# Child documents
curl -X POST "localhost:9200/blog_parent_child/_doc/101?routing=1&pretty" -H 'Content-Type: application/json' -d'
{
  "comment_text": "Great tutorial!",
  "commenter": "Alice",
  "date": "2024-01-15",
  "relation": { "name": "comment", "parent": "1" }
}'

curl -X POST "localhost:9200/blog_parent_child/_doc/102?routing=1&pretty" -H 'Content-Type: application/json' -d'
{
  "comment_text": "Very helpful, thanks!",
  "commenter": "Bob",
  "date": "2024-01-16",
  "relation": { "name": "comment", "parent": "1" }
}'
