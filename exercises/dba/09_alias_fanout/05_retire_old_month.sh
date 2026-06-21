#!/bin/bash -eu
# Retiring data is the other half of the pattern. Because each month is its
# own index hidden behind the alias, "expiring April" is a single index
# delete - no document-by-document deletion, no reindex. The alias quietly
# shrinks by one member and the application's queries return one fewer
# month, with no client change.

# First detach April from the alias, THEN delete the index. Detaching first
# means the alias is never pointing at an index that is about to vanish; a
# search through "logs" during the gap simply sees three months instead of
# four. (Deleting the index alone would also remove it from the alias, but
# doing it explicitly keeps the read view consistent for in-flight queries.)
echo "=== detach April from the alias ==="
curl -X POST "localhost:9200/_aliases?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"actions": [
		{ "remove": { "index": "logs-2026.04", "alias": "logs" } }
	]
}'

# Now drop the whole month in one operation. This is the payoff of
# partitioning by index: retention is an index delete, the cheapest possible
# way to remove a large block of data in Elasticsearch.
echo
echo "=== delete the April index ==="
curl -X DELETE "localhost:9200/logs-2026.04?pretty"

# Confirm the alias now spans one fewer month and a fan-out search no longer
# returns April documents.
echo
echo "=== alias membership after retiring April ==="
curl -s "localhost:9200/_cat/aliases/logs?v&h=alias,index,is_write_index&s=index"

echo
echo "=== documents still visible through 'logs' (April is gone) ==="
curl -s -X GET "localhost:9200/logs/_search?filter_path=hits.total,hits.hits._index" \
	-H 'Content-Type: application/json' -d'{ "query": { "match_all": {} } }'
echo
