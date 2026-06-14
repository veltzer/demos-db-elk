#!/bin/bash -eu
# Asynchronous reindex with task tracking.
#
# For a small index a blocking reindex is fine. For a large one (millions of
# docs) you do NOT want the HTTP connection held open for minutes or hours.
# Passing wait_for_completion=false makes Elasticsearch start the reindex in
# the background and return immediately with a TASK ID. You then poll the
# Tasks API to watch progress and learn when it finishes.
#
# Make a fresh destination so the script is re-runnable.
curl -X DELETE "localhost:9200/products_v1_async?pretty" 2>/dev/null || true

# Kick off the reindex in the background. The response looks like:
#   { "task": "nodeId:taskNumber" }
echo "=== start async reindex ==="
RESPONSE=$(curl -s -X POST \
	"localhost:9200/_reindex?wait_for_completion=false" \
	-H 'Content-Type: application/json' -d'
{
	"source": { "index": "products_v1" },
	"dest":   { "index": "products_v1_async" }
}')
echo "$RESPONSE"

# Extract the task id from the JSON response (no jq dependency: grep+cut).
TASK_ID=$(echo "$RESPONSE" | grep -o '"task"[^,}]*' | cut -d'"' -f4)
echo
echo "task id: $TASK_ID"

# Poll the task. GET /_tasks/<id> returns "completed": true/false plus a
# "status" block with created/total/batches counters. On a tiny index this
# is already done, but on a real one you would loop until completed is true.
echo
echo "=== GET /_tasks/$TASK_ID ==="
curl -s "localhost:9200/_tasks/${TASK_ID}?pretty"

# You can also list every running reindex task across the cluster. This is
# how a DBA finds a runaway reindex someone else started.
echo
echo "=== all running reindex tasks ==="
curl -s "localhost:9200/_tasks?actions=*reindex&detailed=true&pretty"

# To abort a still-running reindex you would cancel its task:
#   curl -X POST "localhost:9200/_tasks/<task_id>/_cancel?pretty"
echo
echo "(cancel a running reindex with: POST /_tasks/<id>/_cancel)"
