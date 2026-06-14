#!/bin/bash -eu
# SIMULATE templates before any index is created. This is the safe way for
# a DBA to confirm exactly what settings and mappings a new index would
# receive WITHOUT actually creating the index. Two endpoints exist.

# (1) _simulate_index/<name> - given a concrete index NAME, show which
# templates match and the fully resolved configuration. Because the name is
# "logs-audit-2024", both logs-template and logs-audit-template match by
# pattern, but the higher-priority audit template wins. Look for:
#   - "overlapping": the templates that matched but were NOT chosen.
#   - "template": the merged settings/mappings/aliases that would apply.
# Expect number_of_replicas = 2 (from the audit template) plus the
# audit-specific "actor"/"action" fields AND the shared log fields.
echo "=== simulate concrete index name: logs-audit-2024 ==="
curl -X POST "localhost:9200/_index_template/_simulate_index/logs-audit-2024?pretty"

# (2) Same call for a plain "logs-2024" index, which only matches the
# lower-priority logs-template. Expect number_of_replicas = 1 and the
# "host" field, but NO "actor"/"action".
echo
echo "=== simulate concrete index name: logs-2024 ==="
curl -X POST "localhost:9200/_index_template/_simulate_index/logs-2024?pretty"

# (3) _simulate with a template BODY - try out a candidate index template
# WITHOUT saving it. Useful for reviewing a change before you PUT it. Here
# we composed_of the existing components and override the refresh interval.
echo
echo "=== simulate an unsaved candidate template body ==="
curl -X POST "localhost:9200/_index_template/_simulate?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index_patterns": ["logs-*"],
	"composed_of": ["common-settings", "logs-mappings"],
	"priority": 100,
	"template": {
		"settings": {
			"index": {
				"refresh_interval": "30s"
			}
		}
	}
}'
