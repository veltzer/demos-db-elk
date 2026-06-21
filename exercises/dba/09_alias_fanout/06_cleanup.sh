#!/bin/bash -eu
# Remove everything this exercise created. Aliases disappear automatically
# when their last backing index is deleted, so we only need to delete the
# indices. We delete by EXACT name rather than a "logs-*" wildcard so that
# on a shared cluster we never sweep up someone else's logs indices.
# (Elasticsearch 8+ rejects wildcard DELETE by default anyway via
# action.destructive_requires_name.) Missing indices return 404, which
# ignore_unavailable=true swallows, so this is safe to run repeatedly.
echo "=== deleting indices ==="
for idx in logs-2026.04 logs-2026.05 logs-2026.06 logs-2026.07; do
	curl -X DELETE "localhost:9200/${idx}?ignore_unavailable=true" || true
	echo
done

echo
echo "=== remaining exercise aliases (should be empty) ==="
curl -s "localhost:9200/_cat/aliases/logs,logs-errors?v" || true

echo
echo "=== remaining exercise indices (should be empty) ==="
curl -s "localhost:9200/_cat/indices/logs-2026.*?v&ignore_unavailable=true" || true
