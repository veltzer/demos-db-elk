#!/bin/bash -eu
# List indices
curl -X GET "localhost:9200/_cat/indices?v&pretty"

# Should see indices like: system-logs-2024.01.XX
