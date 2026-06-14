#!/bin/bash -eu
# Create the "logs_sharded" index demonstrating explicit shard/replica
# settings. As a DBA you almost always set these two numbers explicitly
# rather than relying on defaults, because:
#
#   number_of_shards   - FIXED at creation time. It controls how the data
#                        is divided into primary shards. You CANNOT change
#                        it later without _shrink / _split / reindex.
#   number_of_replicas - DYNAMIC. Copies of each primary for redundancy
#                        and read throughput. Can be changed at runtime.
#
# We deliberately create 4 primary shards here so later steps can _shrink
# it down to 2 (or 1) and _split it up to 8. We also set a factor-friendly
# number_of_routing_shards so _split has room to work.
curl -s -X PUT "localhost:9200/logs_sharded?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"settings": {
		"index": {
			"number_of_shards": 4,
			"number_of_replicas": 1,
			"number_of_routing_shards": 32
		}
	},
	"mappings": {
		"properties": {
			"timestamp":  { "type": "date" },
			"level":      { "type": "keyword" },
			"service":    { "type": "keyword" },
			"host":       { "type": "keyword" },
			"message":    { "type": "text" },
			"latency_ms": { "type": "float" },
			"status":     { "type": "integer" }
		}
	}
}'

echo "=== index settings ==="
curl -s -X GET "localhost:9200/logs_sharded/_settings?pretty"
