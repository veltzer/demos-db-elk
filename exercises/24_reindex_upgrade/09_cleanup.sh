#!/bin/bash -eu
# Remove every index and alias created by this exercise so you can start
# fresh. Safe to run at any time; missing indices are ignored.
#
# Also make sure shard allocation is back to its default in case you ran the
# rolling-upgrade runbook and stopped partway through.
echo "=== deleting exercise indices ==="
for idx in \
	products_v1 \
	products_v1_copy \
	products_v1_async \
	products_v2 \
	products_transformed \
	products_conflict \
	products_src \
	products_from_remote \
	orders_v1 \
	orders_v2; do
	curl -s -X DELETE "localhost:9200/${idx}" >/dev/null 2>&1 || true
	echo "  deleted ${idx} (if it existed)"
done

# Aliases are removed automatically with their backing indices, but reset
# the allocation setting just in case the runbook left it restricted.
echo
echo "=== re-enabling shard allocation (reset to default) ==="
curl -X PUT "localhost:9200/_cluster/settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"persistent": {
		"cluster.routing.allocation.enable": null
	}
}'

echo
echo "=== remaining indices ==="
curl -s "localhost:9200/_cat/indices?v"
