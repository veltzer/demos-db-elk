#!/bin/bash -eu
# Investigate unassigned / relocating shards with the cluster allocation
# explain API, and manually reroute a shard.
#
# When a shard is UNASSIGNED (sitting at yellow/red), the most useful single
# command in Elasticsearch is _cluster/allocation/explain: it tells you the
# EXACT reason a shard cannot be placed on each node (disk watermark hit,
# allocation filtering, awaiting recovery, etc.).

# First, list any unassigned shards so we know whether there is anything to
# explain. On a single-node cluster, replicas are the usual suspects.
echo "=== currently unassigned shards (if any) ==="
curl -s -X GET \
	"localhost:9200/_cat/shards?v&h=index,shard,prirep,state,unassigned.reason&s=state" \
	| grep -E 'UNASSIGNED|index' || echo "(none unassigned)"

# Plain explain with no body asks ES to pick an arbitrary unassigned shard
# and explain it. If everything is assigned it returns a 400 with a helpful
# message, which is why we tolerate a non-zero body here.
echo
echo "=== allocation explain (arbitrary unassigned shard) ==="
curl -s -X GET "localhost:9200/_cluster/allocation/explain?pretty" \
	-H 'Content-Type: application/json' -d'{}' || true

# You can also explain a SPECIFIC shard by index/shard/primary. This is what
# you reach for when one named index is yellow and you want the why.
echo
echo "=== allocation explain for logs_sharded shard 0 (primary) ==="
curl -s -X GET "localhost:9200/_cluster/allocation/explain?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index": "logs_sharded",
	"shard": 0,
	"primary": true
}' || true

# _cluster/reroute lets a DBA take manual control of shard placement. The
# most common safe use is ?retry_failed=true, which asks ES to retry shards
# that hit the max allocation-retry limit (e.g. after a transient disk-full
# that has since been cleared). This does NOT force anything dangerous.
echo
echo "=== retry any failed allocations ==="
curl -s -X POST "localhost:9200/_cluster/reroute?retry_failed=true&pretty" \
	| grep -E '"acknowledged"' || true

# Show the cluster-wide picture one more time so the effect is visible.
echo
echo "=== cluster health summary ==="
curl -s -X GET "localhost:9200/_cluster/health?pretty" \
	| grep -E '"status"|active_shards|unassigned_shards|relocating_shards'
