#!/bin/bash -eu
# Reset an Elasticsearch server back to a near-pristine state.
#
# This DELETES all user data and non-default configuration:
#   - every non-system index (names not starting with ".")
#   - all index and component templates
#   - all legacy (_template) templates
#   - all ILM policies
#   - all ingest pipelines
#   - all snapshot repositories (the repos, not remote snapshot files)
#   - any unassigned shards/replicas left on surviving system indices
#
# System/internal indices (".kibana", ".security", etc.) are left alone so
# that Kibana and security keep working.
#
# THIS IS DESTRUCTIVE AND CANNOT BE UNDONE. It is meant for local / lab
# clusters used by these exercises -- never point it at production.
#
# Usage:
#   ./elk_clean.sh            # prompts for confirmation
#   FORCE=1 ./elk_clean.sh    # skip the prompt (for automation)
#   ES_URL=http://host:9200 ./elk_clean.sh
ES_URL="${ES_URL:-http://localhost:9200}"
FORCE="${FORCE:-0}"

echo "This will DELETE all user indices and non-default config on:"
echo "    ${ES_URL}"
if [ "${FORCE}" != "1" ]; then
	read -r -p "Type 'yes' to continue: " answer
	if [ "${answer}" != "yes" ]; then
		echo "aborted."
		exit 1
	fi
fi

# Helper: DELETE a path and print a short status line, never abort on a 404.
del() {
	echo "--- DELETE $1"
	curl -s -o /dev/null -w "    http %{http_code}\n" -X DELETE "${ES_URL}$1" || true
}

# 1) User indices. The "*,-.*" pattern matches everything except names that
#    start with a dot, so system indices survive. expand_wildcards=open,closed
#    makes sure closed indices are caught too.
echo "=== deleting user indices ==="
del "/*,-.*?expand_wildcards=open,closed"

# 2) Composable index templates and component templates.
echo "=== deleting index templates ==="
for name in $(curl -s "${ES_URL}/_index_template" \
	| grep -o '"name":"[^"]*"' | cut -d'"' -f4); do
	del "/_index_template/${name}"
done
for name in $(curl -s "${ES_URL}/_component_template" \
	| grep -o '"name":"[^"]*"' | cut -d'"' -f4); do
	del "/_component_template/${name}"
done

# 3) Legacy templates (the older _template API).
echo "=== deleting legacy templates ==="
for name in $(curl -s "${ES_URL}/_template" \
	| grep -o '"[^"]*":{' | cut -d'"' -f2); do
	case "${name}" in
		.*) ;;  # skip internal templates
		*) del "/_template/${name}" ;;
	esac
done

# 4) ILM policies.
echo "=== deleting ILM policies ==="
for name in $(curl -s "${ES_URL}/_ilm/policy" \
	| grep -o '"[^"]*":{"version"' | cut -d'"' -f2); do
	del "/_ilm/policy/${name}"
done

# 5) Ingest pipelines.
echo "=== deleting ingest pipelines ==="
for name in $(curl -s "${ES_URL}/_ingest/pipeline" \
	| grep -o '"[^"]*":{"' | cut -d'"' -f2); do
	del "/_ingest/pipeline/${name}"
done

# 6) Snapshot repositories.
echo "=== deleting snapshot repositories ==="
for name in $(curl -s "${ES_URL}/_snapshot" \
	| grep -o '"[^"]*":{"type"' | cut -d'"' -f2); do
	del "/_snapshot/${name}"
done

# 7) Clear leftover unassigned shards/replicas. After the user indices are
#    gone, the usual cause of a yellow cluster is unallocated REPLICAS of the
#    surviving system indices (a single-node cluster can't place them). Setting
#    number_of_replicas=0 on all remaining indices removes those replicas, so
#    there are no unassigned shards left and the cluster goes green.
echo "=== setting replicas to 0 on remaining indices ==="
curl -s -o /dev/null -w "    http %{http_code}\n" \
	-X PUT "${ES_URL}/_all/_settings?expand_wildcards=all" \
	-H 'Content-Type: application/json' \
	-d '{"index":{"number_of_replicas":0}}' || true

# Ask the master to retry any allocations that previously hit a limit, so
# anything still recoverable gets assigned immediately rather than later.
echo "=== retrying failed shard allocations ==="
curl -s -o /dev/null -w "    http %{http_code}\n" \
	-X POST "${ES_URL}/_cluster/reroute?retry_failed=true" || true

echo "=== done. remaining indices: ==="
curl -s "${ES_URL}/_cat/indices?v&h=health,index,docs.count" || true

echo "=== cluster health ==="
curl -s "${ES_URL}/_cluster/health?pretty" \
	| grep -E '"status"|"unassigned_shards"' || true
