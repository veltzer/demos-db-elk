#!/bin/bash -eu
# Change the replica count at runtime and watch cluster health react.
#
# number_of_replicas is a DYNAMIC setting: unlike number_of_shards you can
# change it on a live index with zero downtime. Adding replicas improves read
# throughput and redundancy; removing them frees disk and can turn a yellow
# index green on a single-node cluster.

echo "=== health BEFORE change ==="
curl -s -X GET "localhost:9200/_cluster/health/logs_sharded?pretty" \
	| grep -E '"status"|"number_of_replicas"|unassigned_shards' || true

# Push the replica count up to 2. On a single-node cluster these extra
# replicas have nowhere to go, so the index goes (or stays) YELLOW with
# UNASSIGNED replica shards. On a multi-node cluster ES allocates them and
# the index returns to GREEN once recovery completes.
echo
echo "=== setting number_of_replicas = 2 ==="
curl -s -X PUT "localhost:9200/logs_sharded/_settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index": {
		"number_of_replicas": 2
	}
}'

echo
echo "=== health AFTER raising replicas (expect more UNASSIGNED on 1 node) ==="
curl -s -X GET "localhost:9200/_cluster/health/logs_sharded?pretty" \
	| grep -E '"status"|unassigned_shards' || true

# On a single-node dev box the only way to get back to GREEN is to drop
# replicas to 0 (no copies => nothing left unassigned). In production you
# would instead add data nodes so the replicas can be allocated.
echo
echo "=== setting number_of_replicas = 0 (forces green on a single node) ==="
curl -s -X PUT "localhost:9200/logs_sharded/_settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index": {
		"number_of_replicas": 0
	}
}'

# Wait for the cluster to settle, then confirm the colour.
echo
echo "=== waiting for green ==="
curl -s -X GET \
	"localhost:9200/_cluster/health/logs_sharded?wait_for_status=green&timeout=30s&pretty" \
	| grep -E '"status"|unassigned_shards' || true
