#!/bin/bash -eu
# Check Elasticsearch status
curl -X GET "localhost:9200/_cluster/health?pretty"

# Should return cluster status
