#!/bin/bash -eu
# Split "logs_sharded" (4 primaries) up into "logs_split" (8 primaries).
#
# The _split API is the tool for FIXING an undersharded index: it divides
# each primary shard into several new primaries so the index can grow and
# spread across more nodes.
#
# Hard rules ES enforces for _split:
#   1. The target primary count must be a MULTIPLE of the source count
#      (4 -> 8, 4 -> 12, ...). The split factor also has to divide
#      index.number_of_routing_shards, which is fixed at creation time.
#      We set number_of_routing_shards=32 in 01_create_index.sh, which
#      leaves plenty of room (4 -> 8 -> 16 -> 32 are all valid targets).
#   2. The source index must be made READ-ONLY for the duration.
#   3. Unlike _shrink, the shards do NOT need to be gathered on one node.
#
# This script performs the full correct procedure.

SRC="logs_sharded"
DST="logs_split"

# Clean up any previous run so the script is re-runnable.
curl -s -X DELETE "localhost:9200/${DST}" >/dev/null 2>&1 || true

# Step 1: make the source index read-only (block writes).
echo "=== step 1: make ${SRC} read-only ==="
curl -s -X PUT "localhost:9200/${SRC}/_settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"settings": {
		"index.blocks.write": true
	}
}'

# Step 2: run the split. Target shard count must be a multiple of 4 and must
# divide number_of_routing_shards (32). We reset the write block on the new
# index so it is writable immediately.
echo
echo "=== step 2: split ${SRC} (4) -> ${DST} (8) ==="
curl -s -X POST "localhost:9200/${SRC}/_split/${DST}?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"settings": {
		"index.number_of_shards": 8,
		"index.number_of_replicas": 0,
		"index.blocks.write": null
	}
}'

echo
echo "=== step 3: wait for the split index to go green ==="
curl -s -X GET \
	"localhost:9200/_cluster/health/${DST}?wait_for_status=green&timeout=60s&pretty" \
	| grep -E '"status"' || true

# Step 4: lift the read-only block on the source so it is writable again.
echo
echo "=== step 4: make source writable again ==="
curl -s -X PUT "localhost:9200/${SRC}/_settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index": {
		"blocks.write": null
	}
}'

echo
echo "=== result: primary shard counts ==="
curl -s -X GET \
	"localhost:9200/_cat/shards/${SRC},${DST}?v&h=index,shard,prirep,docs,store&s=index,shard"
