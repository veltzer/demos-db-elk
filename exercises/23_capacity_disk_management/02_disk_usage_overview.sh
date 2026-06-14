#!/bin/bash -eu
# Where is my disk going? This is the first thing a DBA looks at during a
# capacity review or a "disk full" incident. Three views, from coarse to fine.

# _cat/allocation shows, PER DATA NODE, how many shards it holds and how much
# disk those shards consume vs how much disk is free on the filesystem that
# backs the Elasticsearch data path. The disk.percent column is the number the
# watermark thresholds (85/90/95) are compared against. Watch it closely.
echo "=== disk allocation per node (used / avail / percent) ==="
curl -s -X GET \
	"localhost:9200/_cat/allocation?v&h=node,shards,disk.indices,disk.used,disk.avail,disk.total,disk.percent"

# _cat/indices sorted by store size, biggest first, in gigabytes. This tells
# you WHICH indices are eating the disk so you know what to forcemerge, shrink,
# delete via ILM, or move to a cheaper tier. bytes=gb forces a uniform unit so
# the numbers sort correctly (without it "9mb" sorts after "10gb").
echo
echo "=== largest indices (store size descending, in GB) ==="
curl -s -X GET \
	"localhost:9200/_cat/indices?v&s=store.size:desc&bytes=gb&h=index,health,pri,rep,docs.count,store.size,pri.store.size"

# _stats/store drills into a single index. store.size_in_bytes is the total
# on-disk size INCLUDING replicas; primaries.store is just the primary copies.
# The difference is the cost of your replication factor.
echo
echo "=== detailed store stats for capacity_demo ==="
curl -s -X GET "localhost:9200/capacity_demo/_stats/store?pretty"
