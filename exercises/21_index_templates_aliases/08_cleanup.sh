#!/bin/bash -eu
# Remove everything this exercise created: indices, aliases, the composable
# index templates, and the component templates. Aliases are deleted
# automatically when their backing index is deleted, so we only need to
# remove indices and the templates.

# Delete the demo indices. Elasticsearch 8+ rejects wildcard DELETE by
# default (action.destructive_requires_name), so resolve names first. The
# "|| true" guards against an empty list on a clean system.
echo "=== deleting indices ==="
for idx in $(curl -s "localhost:9200/_cat/indices/logs-*,app-*?h=index" || true); do
	curl -X DELETE "localhost:9200/${idx}"
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
curl -X DELETE "localhost:9200/_component_template/logs-mappings?pretty" || true
curl -X DELETE "localhost:9200/_component_template/common-settings?pretty" || true

echo
echo "=== remaining logs-/app- indices (should be empty) ==="
curl -s "localhost:9200/_cat/indices/logs-*,app-*?v" || true
