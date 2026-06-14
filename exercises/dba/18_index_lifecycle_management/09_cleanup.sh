#!/bin/bash -eu
# Remove everything this exercise created. Safe to re-run: every command is
# allowed to fail (the object may already be gone) so we do NOT want -e to abort
# the whole script here — temporarily relax errexit.
set +e

echo "=== deleting data stream 'logs-stream' (and its backing indices) ==="
curl -s -X DELETE "localhost:9200/_data_stream/logs-stream"

echo
echo "=== deleting rollover-alias backing indices 'logs-*' ==="
curl -s -X DELETE "localhost:9200/logs-*"

echo
echo "=== deleting fast-demo indices 'fastlogs-*' ==="
curl -s -X DELETE "localhost:9200/fastlogs-*"

echo
echo "=== deleting index templates ==="
curl -s -X DELETE "localhost:9200/_index_template/logs-template"
curl -s -X DELETE "localhost:9200/_index_template/logs-stream-template"
curl -s -X DELETE "localhost:9200/_index_template/fast-ilm-template"

echo
echo "=== deleting component templates ==="
curl -s -X DELETE "localhost:9200/_component_template/logs-settings"
curl -s -X DELETE "localhost:9200/_component_template/logs-mappings"

echo
echo "=== deleting ILM policies ==="
curl -s -X DELETE "localhost:9200/_ilm/policy/logs-policy"
curl -s -X DELETE "localhost:9200/_ilm/policy/fast-ilm-demo"

echo
echo "=== resetting the ILM poll interval back to its default ==="
curl -s -X PUT "localhost:9200/_cluster/settings" \
	-H 'Content-Type: application/json' -d'
{
	"persistent": {
		"indices.lifecycle.poll_interval": null
	}
}'

echo
echo "cleanup complete."
