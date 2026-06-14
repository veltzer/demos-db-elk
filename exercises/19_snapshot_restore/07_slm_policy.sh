#!/bin/bash -eu
# Snapshot Lifecycle Management (SLM): let Elasticsearch take and prune
# snapshots automatically on a schedule, instead of you running cron jobs
# that call the snapshot API.

REPO="my_fs_repo"
POLICY="daily-snapshots"

# --- create / update the SLM policy -----------------------------------
# schedule  : a cron expression (seconds minutes hours day month weekday).
#             "0 30 1 * * ?" means 01:30 every day.
# name       : the snapshot name template. <...> is a date-math pattern, so
#             each snapshot gets a timestamped, unique name.
# repository : which repository to write into (registered in step 01).
# config     : the same body you would PUT when taking a snapshot by hand.
# retention  : automatic pruning of old snapshots:
#               expire_after  - delete snapshots older than this age
#               min_count     - always keep at least this many
#               max_count     - never keep more than this many
echo "=== create SLM policy ${POLICY} ==="
curl -s -X PUT "localhost:9200/_slm/policy/${POLICY}?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"schedule": "0 30 1 * * ?",
	"name": "<daily-snap-{now/d}>",
	"repository": "my_fs_repo",
	"config": {
		"indices": ["*"],
		"include_global_state": true
	},
	"retention": {
		"expire_after": "30d",
		"min_count": 5,
		"max_count": 50
	}
}'

# --- run the policy NOW (do not wait for the schedule) ----------------
# _execute triggers the policy immediately and returns the snapshot name
# it created. This is how you smoke-test a new policy.
echo "=== execute policy now ==="
curl -s -X POST "localhost:9200/_slm/policy/${POLICY}/_execute?pretty"

# Give the on-demand snapshot a moment to register before we read state.
sleep 2

# --- inspect the policy -----------------------------------------------
# The policy doc includes last_success / last_failure and the next
# scheduled run time, which is what you monitor to know backups are alive.
echo "=== GET policy (state, last run, next run) ==="
curl -s -X GET "localhost:9200/_slm/policy/${POLICY}?pretty"

# --- cluster-wide SLM statistics --------------------------------------
# _slm/stats aggregates taken / failed / deleted counts across all
# policies. Alert if snapshots_failed or snapshot_deletion_failures climb.
echo "=== GET SLM stats ==="
curl -s -X GET "localhost:9200/_slm/stats?pretty"
