#!/bin/bash -eu
curl -X DELETE "localhost:9200/blog_nested?pretty"
curl -X DELETE "localhost:9200/blog_parent_child?pretty"
