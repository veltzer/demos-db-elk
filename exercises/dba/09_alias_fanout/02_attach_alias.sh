#!/bin/bash -eu
# Hide all the monthly indices behind ONE alias. After this script runs, an
# application that searches "logs" transparently searches every monthly
# index at once, and an application that writes to "logs" writes to exactly
# one of them. The application never names a month.

# Attach a READ alias "logs" to all three months in a SINGLE atomic call.
# A search through "logs" now fans out to every member index and merges the
# results, exactly as if you had written "logs-2026.04,logs-2026.05,..." by
# hand - but the client never has to know or maintain that list.
echo "=== attach read alias 'logs' to every month ==="
curl -X POST "localhost:9200/_aliases?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"actions": [
		{ "add": { "index": "logs-2026.04", "alias": "logs" } },
		{ "add": { "index": "logs-2026.05", "alias": "logs" } },
		{ "add": { "index": "logs-2026.06", "alias": "logs" } }
	]
}'

# An alias that spans several indices is ambiguous for WRITES: if you POST a
# document to "logs", Elasticsearch cannot guess which of the three indices
# should receive it and rejects the write. To make the alias writable we
# designate exactly ONE member as the write index with is_write_index:true.
# Reads still fan out across all members; writes all land in this one. This
# is the same mechanism rollover and data streams use under the hood.
echo
echo "=== mark the newest month as the single write index ==="
curl -X POST "localhost:9200/_aliases?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"actions": [
		{ "add": { "index": "logs-2026.06", "alias": "logs", "is_write_index": true } }
	]
}'

# Show the alias membership. Note "logs" maps to three indices, exactly one
# of which has is_write_index true (the "w" / write column in _cat/aliases).
echo
echo "=== alias membership (one alias -> three indices) ==="
curl -s "localhost:9200/_cat/aliases/logs?v&h=alias,index,is_write_index&s=index"

# Prove the fan-out: a single match_all through the alias returns documents
# from ALL three months, not just the write index.
echo
echo "=== search through the alias (expect 3 hits, one per month) ==="
curl -X GET "localhost:9200/logs/_search?pretty&filter_path=hits.total,hits.hits._index" \
	-H 'Content-Type: application/json' -d'
{ "query": { "match_all": {} } }'

# Prove the write routing: a document written to the alias lands in the
# write index (logs-2026.06) only.
echo
echo "=== write through the alias (lands in the write index only) ==="
curl -X POST "localhost:9200/logs/_doc?pretty&filter_path=_index,result" \
	-H 'Content-Type: application/json' -d'
{ "@timestamp": "2026-06-20T09:00:00Z", "level": "INFO", "service": "api", "message": "written via alias" }'
