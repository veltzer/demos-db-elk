#!/bin/bash -eu
# Remove everything this exercise created. Safe to re-run: every command is
# allowed to fail (the object may already be gone) so we do NOT want -e to abort
# the whole script here — temporarily relax errexit.
set +e

# Delete every index matching a pattern. We cannot just DELETE "logs-*": modern
# Elasticsearch defaults action.destructive_requires_name=true, which forbids
# wildcard (and _all) deletes for safety. So we expand the pattern to concrete
# index names via _cat/indices and delete each one explicitly.
delete_indices() {
	local pattern="$1"
	local names
	names=$(curl -s "localhost:9200/_cat/indices/${pattern}?h=index" | tr -d ' ')
	if [ -z "${names}" ]; then
		echo "(no indices matching '${pattern}')"
		return
	fi
	for idx in ${names}; do
		echo "deleting index '${idx}'"
		curl -s -X DELETE "localhost:9200/${idx}" >/dev/null
	done
}

echo "=== deleting data stream 'logs-stream' (and its backing indices) ==="
curl -s -X DELETE "localhost:9200/_data_stream/logs-stream"

echo
echo "=== deleting rollover-alias backing indices 'logs-*' ==="
delete_indices "logs-*"

echo
echo "=== deleting fast-demo indices 'fastlogs-*' ==="
delete_indices "fastlogs-*"

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
