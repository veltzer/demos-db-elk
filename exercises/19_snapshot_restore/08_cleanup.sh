#!/bin/bash -eu
# Tear down everything created by this exercise: snapshots, the SLM policy,
# the repository registration, and the sample indices.
#
# NOTE: deregistering a repository only removes Elasticsearch's reference
# to it. The snapshot files on disk under path.repo are NOT deleted by
# DELETE /_snapshot/<repo>. To free that disk space you must delete the
# individual snapshots first (as we do below) or remove the files manually.

REPO="my_fs_repo"
POLICY="daily-snapshots"

# --- delete individual snapshots --------------------------------------
# You can delete several at once with a comma-separated list. Deleting a
# snapshot only removes segments not needed by any OTHER snapshot, because
# snapshots are incremental and share data.
echo "=== delete snapshots ==="
curl -s -X DELETE "localhost:9200/_snapshot/${REPO}/snap_all,snap_customers?pretty" || true

# SLM-created snapshots match daily-snap-*; delete them too.
echo "=== delete SLM-created snapshots ==="
curl -s -X DELETE "localhost:9200/_snapshot/${REPO}/daily-snap-*?pretty" || true

# --- delete the SLM policy --------------------------------------------
echo "=== delete SLM policy ${POLICY} ==="
curl -s -X DELETE "localhost:9200/_slm/policy/${POLICY}?pretty" || true

# --- deregister the repository ----------------------------------------
echo "=== deregister repository ${REPO} ==="
curl -s -X DELETE "localhost:9200/_snapshot/${REPO}?pretty" || true

# --- delete the sample indices ----------------------------------------
echo "=== delete sample indices ==="
curl -s -X DELETE "localhost:9200/customers,orders,restored_customers?pretty" || true

echo "=== done ==="
