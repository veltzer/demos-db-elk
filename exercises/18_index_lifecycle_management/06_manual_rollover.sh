#!/bin/bash -eu
# Manually trigger a rollover and observe the new backing index.
#
# ILM rolls indices over automatically when the hot-phase conditions are met,
# but you can force a rollover on demand. This works on BOTH a rollover alias
# and a data stream (the target name is the same in either case).
#
# First, index a document so the current write index is non-empty (rollover on
# an empty index is a no-op by default). Then call _rollover.
#
# Note the literal TABS inside each heredoc JSON body.

echo "=== indexing one document into the 'logs' alias ==="
curl -X POST "localhost:9200/logs/_doc?refresh=true&pretty" \
	-H 'Content-Type: application/json' -d'
{
	"@timestamp": "2026-06-14T10:00:00Z",
	"message": "first log line before rollover",
	"level": "info",
	"service": "demo"
}'

echo
echo "=== backing indices BEFORE rollover ==="
curl -s "localhost:9200/_cat/indices/logs-*?v&s=index"

echo
echo "=== forcing rollover of alias 'logs' ==="
# An empty body forces an UNCONDITIONAL rollover: the alias always moves to a
# fresh backing index. You may instead pass "conditions" and only roll over if
# one of them is met (that is exactly what ILM does for you automatically).
curl -X POST "localhost:9200/logs/_rollover?pretty"

echo
echo "=== backing indices AFTER rollover (note 'logs-000002') ==="
curl -s "localhost:9200/_cat/indices/logs-*?v&s=index"

echo
echo "Confirm the write index moved to the new index:"
echo "  curl -s 'localhost:9200/_alias/logs?pretty'"
