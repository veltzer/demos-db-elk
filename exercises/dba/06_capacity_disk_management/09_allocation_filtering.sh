#!/bin/bash -eu
# Allocation filtering and awareness let a DBA control WHERE shards land. This
# is the foundation of hot/warm/cold tiering and of rack/zone fault tolerance,
# and it is directly relevant to capacity: you steer big/old indices onto
# cheaper, larger-disk nodes and keep hot indices on fast nodes.
#
# Two mechanisms:
#   1. Per-INDEX allocation filtering: index.routing.allocation.{require,
#      include,exclude}.<attr> pins an index to nodes that match a node
#      attribute (e.g. node.attr.data=warm set in elasticsearch.yml).
#   2. Cluster-wide allocation AWARENESS: cluster.routing.allocation.awareness
#      .attributes spreads each shard's primary+replicas across distinct values
#      of an attribute (e.g. across racks/zones) so one failure domain cannot
#      take down all copies.

# --- 1. Per-index allocation filtering (hot/warm example) ---------------------
# Ask ES to place capacity_demo only on nodes tagged node.attr.data=warm. On a
# single dev node with no such tag this is harmless: the setting is recorded
# but, with one node, the shard stays where it is. In production this is how an
# index is migrated onto the warm tier.
echo "=== pin capacity_demo to warm-tier nodes (require data=warm) ==="
curl -s -X PUT "localhost:9200/capacity_demo/_settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index.routing.allocation.require.data": "warm"
}'

# Inspect the routing settings we just wrote.
echo
echo "=== current routing.allocation settings on capacity_demo ==="
curl -s -X GET \
	"localhost:9200/capacity_demo/_settings/index.routing.allocation*?pretty"

# Revert so the demo index can live on any node again.
echo
echo "=== revert the per-index allocation filter ==="
curl -s -X PUT "localhost:9200/capacity_demo/_settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index.routing.allocation.require.data": null
}'

# --- 2. Cluster allocation awareness (zone fault tolerance) -------------------
# Tell the cluster that nodes carry a "zone" attribute and that copies of a
# shard must be spread across zones. (Each node would set node.attr.zone in
# elasticsearch.yml; e.g. node.attr.zone: zone-a.) This is set cluster-wide.
echo
echo "=== enable allocation awareness on the 'zone' attribute ==="
curl -s -X PUT "localhost:9200/_cluster/settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"persistent": {
		"cluster.routing.allocation.awareness.attributes": "zone"
	}
}'

# Show that it took effect.
echo
echo "=== current awareness setting ==="
curl -s -X GET \
	"localhost:9200/_cluster/settings?flat_settings=true&pretty" \
	| grep awareness || echo "(no awareness attributes set)"

# Revert so we leave the cluster in its original state.
echo
echo "=== revert allocation awareness ==="
curl -s -X PUT "localhost:9200/_cluster/settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"persistent": {
		"cluster.routing.allocation.awareness.attributes": null
	}
}'
