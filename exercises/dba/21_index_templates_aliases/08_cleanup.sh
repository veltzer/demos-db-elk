#!/bin/bash -eu
# Remove everything this exercise created: indices, aliases, the composable
# index templates, and the component templates. Aliases are deleted
# automatically when their backing index is deleted, so we only need to
# remove indices and the templates.

# Delete the demo indices. We list the EXACT names this exercise creates
# rather than a "logs-*,app-*" wildcard: on a shared cluster a wildcard would
# also sweep up unrelated indices (for example a rollover demo's logs-000001
# or a client's own app-* indices). Deleting by exact name is safe and still
# idempotent - a missing index just returns 404, which "|| true" swallows.
# (Elasticsearch 8+ also rejects wildcard DELETE by default via
# action.destructive_requires_name, so explicit names are required anyway.)
echo "=== deleting indices ==="
for idx in logs-app-2024 logs-audit-2024 app-000001 app-000002; do
	curl -X DELETE "localhost:9200/${idx}?ignore_unavailable=true" || true
	echo
done

# Delete the composable index templates.
echo "=== deleting index templates ==="
curl -X DELETE "localhost:9200/_index_template/logs-audit-template?pretty" || true
curl -X DELETE "localhost:9200/_index_template/logs-template?pretty" || true

# Delete the component templates. These must be removed AFTER the index
# templates that reference them, or Elasticsearch refuses (a component
# template in use cannot be deleted).
echo "=== deleting component templates ==="
curl -X DELETE "localhost:9200/_component_template/logs-fields?pretty" || true
curl -X DELETE "localhost:9200/_component_template/common-settings?pretty" || true

echo
echo "=== remaining exercise indices (should be empty) ==="
curl -s "localhost:9200/_cat/indices/logs-app-2024,logs-audit-2024,app-000001,app-000002?v&ignore_unavailable=true" || true
