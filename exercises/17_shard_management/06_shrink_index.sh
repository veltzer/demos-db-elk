#!/bin/bash -eu
# Shrink "logs_sharded" (4 primaries) down to "logs_shrunk" (2 primaries).
#
# The _shrink API is the tool for FIXING an oversharded index: it merges
# multiple primary shards into fewer, larger ones without a full reindex.
#
# Hard rules ES enforces for _shrink:
#   1. The target primary count must be a FACTOR of the source count
#      (4 -> 2 or 4 -> 1, but never 4 -> 3).
#   2. The index must be made READ-ONLY for the duration.
#   3. A full copy of EVERY primary shard must sit on ONE single node first
#      (so ES can hard-link the segments into the new shards).
#
# This script performs the full correct procedure end to end.

SRC="logs_sharded"
DST="logs_shrunk"

# Clean up any previous run so the script is re-runnable.
curl -s -X DELETE "localhost:9200/${DST}" >/dev/null 2>&1 || true

# Pick a target node name to gather all shards onto. We just grab the first
# node from _cat/nodes. On a single-node cluster this is that one node.
NODE=$(curl -s "localhost:9200/_cat/nodes?h=name" | head -n1 | tr -d '[:space:]')
echo "Gathering all '${SRC}' shards onto node: ${NODE}"

# Step 1: relocate every primary onto one node AND set the index read-only.
# index.blocks.write=true makes it read-only; routing.allocation.require._name
# pins all shards to the chosen node.
echo "=== step 1: pin shards to one node + make read-only ==="
curl -s -X PUT "localhost:9200/${SRC}/_settings?pretty" \
	-H 'Content-Type: application/json' -d"
{
	\"settings\": {
		\"index.routing.allocation.require._name\": \"${NODE}\",
		\"index.blocks.write\": true
	}
}"

# Wait until the cluster is green for this index, i.e. relocation finished.
echo
echo "=== step 2: wait for relocation to finish ==="
curl -s -X GET \
	"localhost:9200/_cluster/health/${SRC}?wait_for_no_relocating_shards=true&wait_for_status=green&timeout=60s&pretty" \
	| grep -E '"status"|relocating_shards' || true

# Step 3: run the shrink. The target index inherits a fresh shard count and
# we explicitly reset the allocation requirement and the write block so the
# new index is usable normally.
echo
echo "=== step 3: shrink ${SRC} (4) -> ${DST} (2) ==="
curl -s -X POST "localhost:9200/${SRC}/_shrink/${DST}?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"settings": {
		"index.number_of_shards": 2,
		"index.number_of_replicas": 0,
		"index.routing.allocation.require._name": null,
		"index.blocks.write": null
	}
}'

echo
echo "=== step 4: wait for the shrunk index to go green ==="
curl -s -X GET \
	"localhost:9200/_cluster/health/${DST}?wait_for_status=green&timeout=60s&pretty" \
	| grep -E '"status"' || true

# Step 5: lift the read-only block on the SOURCE index so it is writable
# again (shrink leaves the source read-only).
echo
echo "=== step 5: make source writable again ==="
curl -s -X PUT "localhost:9200/${SRC}/_settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index": {
		"blocks.write": null,
		"routing.allocation.require._name": null
	}
}'

echo
echo "=== result: primary shard counts ==="
curl -s -X GET \
	"localhost:9200/_cat/shards/${SRC},${DST}?v&h=index,shard,prirep,docs,store&s=index,shard"
