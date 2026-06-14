#!/bin/bash -eu
# Inspect and control Index Lifecycle Management.
#
# This script is a reference tour of the operational ILM endpoints a DBA uses
# to see where an index sits in its lifecycle and to drive the lifecycle by
# hand when something goes wrong.

echo "=== _ilm/explain : where is each backing index in its lifecycle? ==="
# Shows the policy, current phase/action/step, and timing for every index that
# matches the pattern. This is the first thing to check when an index is "stuck".
curl -s "localhost:9200/logs-*/_ilm/explain?pretty"

echo
echo "=== _ilm/status : is the lifecycle service RUNNING or STOPPED? ==="
curl -s "localhost:9200/_ilm/status?pretty"

echo
echo "=== stopping the ILM service (no index will advance while STOPPED) ==="
# Useful before maintenance so ILM does not move/delete indices underneath you.
curl -X POST "localhost:9200/_ilm/stop?pretty"

echo
echo "=== starting the ILM service again ==="
curl -X POST "localhost:9200/_ilm/start?pretty"

echo
echo "=== _ilm/move : force a specific index to a new step ==="
# Manually advancing an index is an escape hatch for a stuck index. You must
# name the CURRENT step and the NEXT step you want it moved to. The values below
# are illustrative; read them out of _ilm/explain for the real index first.
echo "Example (edit the index name and steps to match _ilm/explain output):"
cat <<'EOF'
  curl -X POST "localhost:9200/_ilm/move/logs-000001?pretty" \
    -H 'Content-Type: application/json' -d'
  {
    "current_step": {
      "phase": "hot",
      "action": "complete",
      "name": "complete"
    },
    "next_step": {
      "phase": "warm"
    }
  }'
EOF
