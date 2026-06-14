#!/bin/bash -eu
# Take snapshots into the repository registered in step 01.
#
# A snapshot is a point-in-time, INCREMENTAL backup. The first snapshot
# copies all segment files; later snapshots only copy segments that
# changed, so they are fast and space-efficient even though each snapshot
# still restores as a complete, standalone copy.

REPO="my_fs_repo"

# --- snapshot 1: ALL indices ------------------------------------------
# wait_for_completion=true makes the call block until the snapshot is done
# and return the final result. In production automation you usually leave
# it false and poll _status instead, so the HTTP call returns immediately.
echo "=== snapshot snap_all (all indices) ==="
curl -s -X PUT "localhost:9200/_snapshot/${REPO}/snap_all?wait_for_completion=true&pretty" \
	-H 'Content-Type: application/json' -d'
{
	"indices": "*",
	"include_global_state": true,
	"metadata": {
		"taken_by": "dba-training",
		"reason": "full cluster backup demo"
	}
}'

# --- snapshot 2: a SELECTIVE snapshot of just one index ---------------
# Use "indices" to back up only specific indices. ignore_unavailable skips
# missing indices instead of failing; include_global_state=false keeps the
# snapshot focused on the listed data only.
echo "=== snapshot snap_customers (customers only) ==="
curl -s -X PUT "localhost:9200/_snapshot/${REPO}/snap_customers?wait_for_completion=true&pretty" \
	-H 'Content-Type: application/json' -d'
{
	"indices": "customers",
	"ignore_unavailable": true,
	"include_global_state": false
}'

# --- detailed status of a snapshot ------------------------------------
# _status shows per-shard progress and byte/file counts. While a snapshot
# is running it reports STARTED; once finished it reports SUCCESS.
echo "=== detailed status of snap_all ==="
curl -s -X GET "localhost:9200/_snapshot/${REPO}/snap_all/_status?pretty"
