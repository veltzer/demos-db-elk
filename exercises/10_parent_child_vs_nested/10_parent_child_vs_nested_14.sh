#!/bin/bash -eu
# Nested: All data in one document
curl -X GET "localhost:9200/blog_nested/_doc/1?pretty"

# Parent-Child: Separate documents
curl -X GET "localhost:9200/blog_parent_child/_doc/1?pretty"
curl -X GET "localhost:9200/blog_parent_child/_doc/101?routing=1&pretty"
