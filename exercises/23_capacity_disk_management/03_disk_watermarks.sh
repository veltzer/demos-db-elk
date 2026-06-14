#!/bin/bash -eu
# Disk watermarks control how Elasticsearch reacts as a data node fills up.
# There are three thresholds, all expressed as a percentage of disk used (you
# can also use absolute sizes like "50gb" of FREE space):
#
#   low        (default 85%) - ES stops allocating NEW shards to this node.
#                              Existing shards stay put. New indices may go
#                              yellow/red if no node is below the low mark.
#   high       (default 90%) - ES actively tries to RELOCATE shards AWAY from
#                              this node to nodes with more free space.
#   flood_stage(default 95%) - ES marks every index that has a shard on this
#                              node as read-only (index.blocks.
#                              read_only_allow_delete = true). Writes are
#                              REJECTED. This is the classic 2am page. See
#                              script 05 for the recovery runbook.
#
# These are CLUSTER-wide settings under cluster.routing.allocation.disk.*.

# View the CURRENT effective values, including the built-in defaults, flattened
# to dotted keys and grep-filtered down to just the watermark settings. Without
# include_defaults you only see values you have explicitly overridden.
echo "=== current watermark settings (incl. defaults) ==="
curl -s -X GET \
	"localhost:9200/_cluster/settings?include_defaults=true&flat_settings=true" \
	| tr ',' '\n' | grep -E "disk.watermark|disk.threshold_enabled" \
	|| echo "(no watermark keys matched - check the raw output below)"

# Now SET more conservative watermarks as a transient override. transient
# settings are lost on a full cluster restart; use "persistent" for values
# that must survive restarts. We give ourselves earlier warning here.
echo
echo "=== setting conservative watermarks (transient) ==="
curl -s -X PUT "localhost:9200/_cluster/settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"transient": {
		"cluster.routing.allocation.disk.watermark.low": "80%",
		"cluster.routing.allocation.disk.watermark.high": "85%",
		"cluster.routing.allocation.disk.watermark.flood_stage": "90%"
	}
}'

# To revert a transient setting back to the default, set it to null.
echo
echo "=== reverting watermarks back to defaults ==="
curl -s -X PUT "localhost:9200/_cluster/settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"transient": {
		"cluster.routing.allocation.disk.watermark.low": null,
		"cluster.routing.allocation.disk.watermark.high": null,
		"cluster.routing.allocation.disk.watermark.flood_stage": null
	}
}'
