#!/bin/bash -eu
# Nested: 1 document total (all comments stored within)
curl -X GET "localhost:9200/blog_nested/_count?pretty"

# Parent-Child: Multiple documents (1 parent + N children)
curl -X GET "localhost:9200/blog_parent_child/_count?pretty"
