#!/bin/bash -eu
# Reproduce the flood-stage read-only block on demand, WITHOUT actually filling
# the disk. When a node crosses the flood_stage watermark, Elasticsearch sets
#   index.blocks.read_only_allow_delete: true
# on the affected indices and starts rejecting writes with a
# "cluster_block_exception". To practice detecting and clearing that block
# safely, we set the same block by hand here. This is a SIMULATION of the
# incident so you can rehearse the recovery runbook in script 05.

# Apply the exact block ES would apply at flood stage.
echo "=== applying read_only_allow_delete block to capacity_demo ==="
curl -s -X PUT "localhost:9200/capacity_demo/_settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index.blocks.read_only_allow_delete": true
}'

# Prove that writes are now rejected. This indexing request should fail with a
# cluster_block_exception (HTTP 429). We do NOT pass -e/--fail so the script
# keeps running and you can read the error body, which is exactly what you
# would see in your application logs during a real incident.
echo
echo "=== attempting a write (expected to be BLOCKED) ==="
curl -s -X POST "localhost:9200/capacity_demo/_doc?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"message": "this write should be rejected while the index is read-only"
}'

echo
echo "Index is now blocked. Run 05_flood_stage_runbook.sh to recover."
