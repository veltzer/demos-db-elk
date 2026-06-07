#!/bin/bash -eu
# Drop the "articles" index.
curl -X DELETE "localhost:9200/articles?pretty"
