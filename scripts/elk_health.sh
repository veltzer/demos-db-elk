#!/bin/bash -eu
# General ELK / Elasticsearch health check.
#
# A quick, dependency-free overview of a cluster using only curl. This is
# the script to reach for first when something feels wrong: it prints the
# cluster health, the node list, any unassigned shards, and a few key
# stats, all against a single endpoint.
#
# Override the target with the ES_URL environment variable, e.g.
#   ES_URL=http://my-host:9200 ./elk_health.sh
ES_URL="${ES_URL:-http://localhost:9200}"

echo "=== target: ${ES_URL} ==="

# Cluster health summary (green / yellow / red).
echo "=== cluster health ==="
curl -s -X GET "${ES_URL}/_cluster/health?pretty"

# One line per node: name, role, heap, cpu, load. The v= asks for a header.
echo "=== nodes ==="
curl -s -X GET "${ES_URL}/_cat/nodes?v&h=name,node.role,heap.percent,ram.percent,cpu,load_1m"

# Any shards that are not assigned, with the reason. Empty output is good.
echo "=== unassigned shards (empty is healthy) ==="
curl -s -X GET "${ES_URL}/_cat/shards?v&h=index,shard,prirep,state,unassigned.reason" | grep -E "UNASSIGNED|INITIALIZING" || echo "(none)"

# Per-index summary: health, doc count, store size.
echo "=== indices ==="
curl -s -X GET "${ES_URL}/_cat/indices?v&h=health,status,index,docs.count,store.size&s=index"

# Pending cluster-level tasks. A growing queue signals a struggling master.
echo "=== pending tasks ==="
curl -s -X GET "${ES_URL}/_cat/pending_tasks?v" || true
