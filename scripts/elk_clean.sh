#!/bin/bash -eu
# Reset an Elasticsearch server back to a near-pristine state, removing ONLY
# the things you created -- never the defaults that Elasticsearch or Kibana
# ship with.
#
# What it deletes:
#   - every non-system index (names not starting with ".")
#   - user-created index templates, component templates and legacy templates
#   - user-created ILM policies
#   - user-created ingest pipelines
#   - user-registered snapshot repositories
#   - any unassigned shards/replicas left on surviving system indices
#
# How "user-created" is decided: Elasticsearch and Kibana tag everything they
# install with "_meta": {"managed": true} (and/or a managing plugin). This
# script SKIPS anything with managed=true, so the built-in templates, ILM
# policies and pipelines (logs, metrics, .deprecation-*, ilm-history-*, the
# Kibana/Fleet objects, etc.) are left untouched. System indices (".kibana",
# ".security", ...) are also preserved.
#
# Requires jq for reliable filtering.
#
# THIS IS DESTRUCTIVE for the things you made and CANNOT BE UNDONE. It is meant
# for local / lab clusters used by these exercises -- never point it at prod.
#
# Usage:
#   ./elk_clean.sh            # prompts for confirmation
#   FORCE=1 ./elk_clean.sh    # skip the prompt (for automation)
#   ES_URL=http://host:9200 ./elk_clean.sh
ES_URL="${ES_URL:-http://localhost:9200}"
FORCE="${FORCE:-0}"

if ! command -v jq >/dev/null 2>&1; then
	echo "error: jq is required (used to skip ES/Kibana managed objects)." >&2
	exit 1
fi

echo "This will DELETE your indices and the config YOU created on:"
echo "    ${ES_URL}"
echo "(Elasticsearch/Kibana managed defaults are preserved.)"
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

# 1) User indices. "*,-.*" matches everything except names starting with a dot,
#    so system indices survive. expand_wildcards catches closed indices too.
echo "=== deleting user indices ==="
del "/*,-.*?expand_wildcards=open,closed"

# 2) Composable index templates -- skip any with _meta.managed == true.
echo "=== deleting user index templates ==="
for name in $(curl -s "${ES_URL}/_index_template" \
	| jq -r '.index_templates[]
		| select((.index_template._meta.managed // false) != true)
		| .name'); do
	del "/_index_template/${name}"
done

# 3) Component templates -- same managed filter.
echo "=== deleting user component templates ==="
for name in $(curl -s "${ES_URL}/_component_template" \
	| jq -r '.component_templates[]
		| select((.component_template._meta.managed // false) != true)
		| .name'); do
	del "/_component_template/${name}"
done

# 4) Legacy templates (_template). These are keyed by name; skip dot-prefixed
#    internal ones and any flagged managed.
echo "=== deleting user legacy templates ==="
for name in $(curl -s "${ES_URL}/_template" \
	| jq -r 'to_entries[]
		| select((.value._meta.managed // false) != true)
		| select(.key | startswith(".") | not)
		| .key'); do
	del "/_template/${name}"
done

# 5) ILM policies -- the built-ins carry _meta.managed == true.
echo "=== deleting user ILM policies ==="
for name in $(curl -s "${ES_URL}/_ilm/policy" \
	| jq -r 'to_entries[]
		| select((.value.policy._meta.managed // false) != true)
		| .key'); do
	del "/_ilm/policy/${name}"
done

# 6) Ingest pipelines -- managed pipelines (Fleet/APM/etc.) set _meta.managed.
echo "=== deleting user ingest pipelines ==="
for name in $(curl -s "${ES_URL}/_ingest/pipeline" \
	| jq -r 'to_entries[]
		| select((.value._meta.managed // false) != true)
		| .key'); do
	del "/_ingest/pipeline/${name}"
done

# 7) Snapshot repositories. These are all user-registered (ES ships none),
#    so every repo here is something you added.
echo "=== deleting snapshot repositories ==="
for name in $(curl -s "${ES_URL}/_snapshot" | jq -r 'keys[]'); do
	del "/_snapshot/${name}"
done

# 8) Clear leftover unassigned shards/replicas. After the user indices are
#    gone, the usual cause of a yellow cluster is unallocated REPLICAS of the
#    surviving system indices (a single-node cluster can't place them). Setting
#    number_of_replicas=0 on the remaining indices removes those replicas so
#    there are no unassigned shards left and the cluster goes green.
echo "=== setting replicas to 0 on remaining indices ==="
curl -s -o /dev/null -w "    http %{http_code}\n" \
	-X PUT "${ES_URL}/_all/_settings?expand_wildcards=all" \
	-H 'Content-Type: application/json' \
	-d '{"index":{"number_of_replicas":0}}' || true

# Ask the master to retry any allocations that previously hit a limit.
echo "=== retrying failed shard allocations ==="
curl -s -o /dev/null -w "    http %{http_code}\n" \
	-X POST "${ES_URL}/_cluster/reroute?retry_failed=true" || true

echo "=== done. remaining indices: ==="
curl -s "${ES_URL}/_cat/indices?v&h=health,index,docs.count" || true

echo "=== cluster health ==="
curl -s "${ES_URL}/_cluster/health?pretty" \
	| grep -E '"status"|"unassigned_shards"' || true
