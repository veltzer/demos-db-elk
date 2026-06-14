#!/bin/bash -eu
# DBA RUNBOOK: "my indices have gone read-only and writes are failing".
#
# Symptom: applications report cluster_block_exception / FORBIDDEN/12/index
# read-only / allow delete (api). Cause: a data node crossed the flood_stage
# disk watermark (default 95% used) and ES set
#   index.blocks.read_only_allow_delete: true
# on every index with a shard on that node.
#
# The block does NOT clear itself the moment disk frees up in older versions,
# and you should never clear it before you have actually freed disk, or you
# will just flood again. Follow these steps IN ORDER.

# STEP 1: Confirm which indices are blocked. Check the per-index settings.
# A blocked index shows "read_only_allow_delete": "true".
echo "=== STEP 1: detect the block ==="
curl -s -X GET \
	"localhost:9200/capacity_demo/_settings/index.blocks.read_only_allow_delete?pretty"

# A cluster-wide sweep for every blocked index (handy when many are affected):
echo
echo "=== blocked indices across the cluster ==="
curl -s -X GET "localhost:9200/_all/_settings/index.blocks*?pretty" \
	| grep -B2 "read_only" || echo "(none blocked)"

# STEP 2: FREE DISK FIRST. In a real incident this is the actual fix, e.g.
# delete old indices (ILM should do this), forcemerge to expunge deletes, move
# indices to a warm/cold tier, or add disk/nodes. We illustrate the cheapest
# win: drop and recreate the demo's expensive field data via forcemerge.
echo
echo "=== STEP 2: free disk (forcemerge to expunge deleted docs) ==="
curl -s -X POST \
	"localhost:9200/capacity_demo/_forcemerge?only_expunge_deletes=true&pretty" \
	|| echo "(forcemerge skipped/failed - in a real incident, delete data here)"

# STEP 3: clear the block. Setting it to null reverts to the default. ONLY do
# this AFTER you are back below the high watermark, otherwise it re-triggers.
echo
echo "=== STEP 3: clear the read-only block ==="
curl -s -X PUT "localhost:9200/capacity_demo/_settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index.blocks.read_only_allow_delete": null
}'

# STEP 4: verify writes work again.
echo
echo "=== STEP 4: verify writes are accepted again ==="
curl -s -X POST "localhost:9200/capacity_demo/_doc?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"message": "recovery confirmed: writes are accepted after clearing the block"
}'
