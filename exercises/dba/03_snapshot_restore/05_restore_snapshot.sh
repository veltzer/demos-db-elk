#!/bin/bash -eu
# Restore data from a snapshot.
#
# KEY RULE: you cannot restore over an open index with the same name. You
# must first delete it or close it, OR restore under a different name using
# rename_pattern / rename_replacement. We demonstrate both approaches.

REPO="my_fs_repo"

# --- full restore: delete then restore --------------------------------
# Simulate losing the orders index, then restore it from snap_all.
echo "=== delete orders (simulate data loss) ==="
curl -s -X DELETE "localhost:9200/orders?pretty"

echo "=== restore orders from snap_all ==="
curl -s -X POST "localhost:9200/_snapshot/${REPO}/snap_all/_restore?wait_for_completion=true&pretty" \
	-H 'Content-Type: application/json' -d'
{
	"indices": "orders",
	"include_global_state": false
}'

echo "=== verify orders restored ==="
curl -s -X GET "localhost:9200/_cat/count/orders?v"

# --- selective restore UNDER A NEW NAME -------------------------------
# rename_pattern is a regex applied to each restored index name; the
# capture groups are substituted into rename_replacement. Here we restore
# "customers" from the snapshot as a NEW index "restored_customers",
# leaving the live "customers" index untouched. This is the safe way to
# inspect a backup without overwriting production.
echo "=== restore customers as restored_customers ==="
curl -s -X POST "localhost:9200/_snapshot/${REPO}/snap_customers/_restore?wait_for_completion=true&pretty" \
	-H 'Content-Type: application/json' -d'
{
	"indices": "customers",
	"rename_pattern": "(.+)",
	"rename_replacement": "restored_$1",
	"include_global_state": false,
	"index_settings": {
		"index.number_of_replicas": 0
	}
}'

echo "=== verify restored_customers ==="
curl -s -X GET "localhost:9200/_cat/count/restored_customers?v"
