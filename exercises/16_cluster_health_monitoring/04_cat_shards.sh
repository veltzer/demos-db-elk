#!/bin/bash -eu
# List shards and hunt for UNASSIGNED shards.
#
# _cat/shards has one row per shard with these key columns:
#   index   - the index the shard belongs to
#   shard   - shard number
#   prirep  - p (primary) or r (replica)
#   state   - STARTED, INITIALIZING, RELOCATING, or UNASSIGNED
#   docs    - document count
#   store   - on-disk size
#   node    - which node holds the shard (empty if unassigned)

# Full shard listing.
echo "=== all shards ==="
curl -s -X GET "http://localhost:9200/_cat/shards?v&h=index,shard,prirep,state,docs,store,node"

# Filter to only the problem shards. UNASSIGNED shards are the ones a DBA
# must explain and fix; they are why a cluster is yellow or red.
echo "=== UNASSIGNED shards only ==="
curl -s -X GET "http://localhost:9200/_cat/shards?v&h=index,shard,prirep,state,unassigned.reason,unassigned.at" \
	| grep -E "UNASSIGNED|^index" || echo "no unassigned shards (cluster is healthy)"

# RELOCATING/INITIALIZING shards indicate the cluster is rebalancing.
echo "=== shards in transition (INITIALIZING / RELOCATING) ==="
curl -s -X GET "http://localhost:9200/_cat/shards?v&h=index,shard,prirep,state,node" \
	| grep -E "INITIALIZING|RELOCATING|^index" || echo "no shards in transition"
