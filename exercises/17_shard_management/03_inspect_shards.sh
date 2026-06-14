#!/bin/bash -eu
# Inspect how shards are distributed across the cluster. These _cat APIs are
# the DBA's bread and butter for shard management. The "v" parameter adds a
# header row; "s=..." sorts the output.

# _cat/shards lists every shard (primary AND replica) in the cluster, which
# node it lives on, its state, doc count and store size. We restrict the
# columns with ?h=... and sort by store size descending so the biggest
# shards float to the top.
echo "=== shards for logs_sharded (index, shard, prirep, docs, store, node) ==="
curl -s -X GET \
	"localhost:9200/_cat/shards/logs_sharded?v&h=index,shard,prirep,docs,store,node&s=store:desc"

# prirep column: 'p' = primary, 'r' = replica. With number_of_replicas=1 you
# should see each shard number twice (one p, one r) on different nodes if you
# have more than one node. On a single node the replicas stay UNASSIGNED and
# the index sits at health=yellow (that is expected and fine for dev).
echo
echo "=== shard state (look for UNASSIGNED replicas on a single node) ==="
curl -s -X GET \
	"localhost:9200/_cat/shards/logs_sharded?v&h=index,shard,prirep,state,unassigned.reason"

# _cat/allocation shows, per node, how many shards it holds and how much disk
# the shards consume vs how much disk is free. This is how you spot a node
# that is unbalanced or running low on disk.
echo
echo "=== allocation per node (shards, disk used/avail) ==="
curl -s -X GET "localhost:9200/_cat/allocation?v"
