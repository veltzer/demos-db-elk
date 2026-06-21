#!/bin/bash -eu
# The same set of indices can sit behind MORE THAN ONE alias, each exposing
# a different view. Here we add a second alias "logs-errors" over the same
# three months, but with a filter so it only ever returns ERROR documents.
# One physical data set, two logical names with different scopes - and the
# application still never references a month.

# Add a FILTERED alias spanning the same three indices. The stored filter is
# silently ANDed onto every search through this alias, so "logs-errors" is a
# read-only view of just the error lines across all months. It costs nothing
# in storage - it is metadata, not a copy.
echo "=== add filtered alias 'logs-errors' over the same months ==="
curl -X POST "localhost:9200/_aliases?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"actions": [
		{ "add": { "index": "logs-2026.04", "alias": "logs-errors", "filter": { "term": { "level": "ERROR" } } } },
		{ "add": { "index": "logs-2026.05", "alias": "logs-errors", "filter": { "term": { "level": "ERROR" } } } },
		{ "add": { "index": "logs-2026.06", "alias": "logs-errors", "filter": { "term": { "level": "ERROR" } } } }
	]
}'

# Searching the plain alias returns every level across all months...
echo
echo "=== 'logs' returns all levels (INFO/WARN/ERROR) ==="
curl -s -X GET "localhost:9200/logs/_search?filter_path=hits.total" \
	-H 'Content-Type: application/json' -d'{ "query": { "match_all": {} } }'

# ...while searching the filtered alias over the exact same indices returns
# only the error documents. The caller writes no query clause for "level";
# the alias supplies it. This is how you hand a team a pre-scoped view
# without trusting every client to remember the filter.
echo
echo
echo "=== 'logs-errors' returns ERROR only, still across all months ==="
curl -s -X GET "localhost:9200/logs-errors/_search?filter_path=hits.total,hits.hits._index,hits.hits._source.level" \
	-H 'Content-Type: application/json' -d'{ "query": { "match_all": {} } }'
echo
