#!/bin/bash -eu
# Rolling upgrade runbook (one node at a time, cluster stays up).
#
# This script is a RUNBOOK, not an automated upgrade. We cannot actually
# upgrade the single running node from inside this exercise, so the steps
# that physically replace the binary (stop / install / start) are echoed as
# instructions, while the API steps a DBA actually runs by hand - health
# checks, deprecation checks, and the allocation enable/disable dance - are
# real, live curl commands you can execute right now.
#
# A rolling upgrade lets the cluster keep serving traffic: you take down,
# upgrade, and rejoin nodes ONE AT A TIME. It is supported between minor
# versions and across one major boundary (e.g. last 7.x -> 8.x). Always
# SNAPSHOT FIRST - if anything goes wrong you restore, you do not improvise.

echo "############################################################"
echo "# PRE-UPGRADE CHECKS (run these before touching any node)  #"
echo "############################################################"

# 1. Cluster must be GREEN before you start. A yellow/red cluster during an
#    upgrade is how you turn one problem into a data-loss incident.
echo
echo "=== 1. cluster health (want status: green) ==="
curl -s "localhost:9200/_cluster/health?pretty"

# 2. SNAPSHOT FIRST. This is non-negotiable. (See exercise 19 for setting up
#    a repository.) Conceptually:
echo
echo "=== 2. take a snapshot FIRST (example - needs a repo) ==="
echo 'curl -X PUT "localhost:9200/_snapshot/my_repo/pre_upgrade_$(date +%s)?wait_for_completion=true"'

# 3. Check for deprecations that will break on the next version. The
#    Migration Deprecations API lists settings/mappings you must fix first.
echo
echo "=== 3. deprecation / migration checks ==="
curl -s "localhost:9200/_migration/deprecations?pretty" || \
	echo "(deprecations API may require a license tier)"

echo
echo "############################################################"
echo "# PER-NODE LOOP (repeat for EACH node, one at a time)      #"
echo "############################################################"

# 4. Disable shard allocation so the cluster does not start frantically
#    rebalancing the moment a node leaves. We allow "primaries" so any
#    primary that has no in-sync replica can still recover.
echo
echo "=== 4. disable shard allocation (before stopping the node) ==="
curl -X PUT "localhost:9200/_cluster/settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"persistent": {
		"cluster.routing.allocation.enable": "primaries"
	}
}'

# 5. Stop indexing if you can, and flush so recovery after restart is fast.
echo
echo "=== 5. (optional) synced/normal flush to speed recovery ==="
curl -X POST "localhost:9200/_flush?pretty"

# 6. Physically upgrade THIS node. These are shell actions, not API calls,
#    so we only print them. Do them on the box being upgraded:
echo
echo "=== 6. stop, upgrade binary, restart THIS node (manual) ==="
echo '  sudo systemctl stop elasticsearch'
echo '  # install the new package / unpack the new archive over $ES_HOME'
echo '  sudo systemctl start elasticsearch'

# 7. Wait for the upgraded node to rejoin and the cluster to leave the
#    "node count dropped" state. Then RE-ENABLE allocation.
echo
echo "=== 7. re-enable shard allocation (after node rejoins) ==="
curl -X PUT "localhost:9200/_cluster/settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"persistent": {
		"cluster.routing.allocation.enable": null
	}
}'

# 8. Wait for GREEN before moving to the next node. The wait_for_status +
#    timeout makes this curl BLOCK until the cluster recovers (or times out).
echo
echo "=== 8. wait for the cluster to go green again ==="
curl -s "localhost:9200/_cluster/health?wait_for_status=green&timeout=300s&pretty"

echo
echo "Cluster is green. Repeat steps 4-8 for the next node until all nodes"
echo "run the new version. Upgrade master-eligible nodes LAST."
