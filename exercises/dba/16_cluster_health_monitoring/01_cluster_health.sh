#!/bin/bash -eu
# Check overall cluster health.
#
# The cluster health status is the single most important signal a DBA
# watches. It is one of three colors:
#   green  - all primary AND replica shards are allocated.
#   yellow - all primaries are allocated, but some replicas are not.
#   red    - at least one PRIMARY shard is not allocated; data is missing.
#
# The plain call returns the cluster-wide summary.
echo "=== cluster-wide health ==="
curl -s -X GET "http://localhost:9200/_cluster/health?pretty"

# level=indices breaks the status down per index, so you can see WHICH
# index is yellow or red rather than just the whole cluster.
echo "=== health per index (level=indices) ==="
curl -s -X GET "http://localhost:9200/_cluster/health?level=indices&pretty"

# level=shards is the most detailed view: status per individual shard.
# Use this when an index is red/yellow and you need the exact shard.
echo "=== health per shard (level=shards) ==="
curl -s -X GET "http://localhost:9200/_cluster/health?level=shards&pretty"
