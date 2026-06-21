#!/bin/bash -eu
# Turn on the search and indexing SLOW LOGS for one index with sensible
# thresholds, then DEMONSTRATE them: run slow queries and print the
# resulting slow-log lines.
#
# Slow logs record individual queries / index operations that exceed a
# time threshold, broken into warn/info/debug/trace tiers. They are the
# best way to catch the specific slow requests hurting a cluster, because
# they log the actual query source.
#
# WHERE DO THE LINES LAND?
#   It depends on the log4j2 slow-log appender. On a classic package
#   install the appender is a rolling FILE in the Elasticsearch logs
#   directory (usually /var/log/elasticsearch/):
#     <cluster>_index_search_slowlog.json
#     <cluster>_index_indexing_slowlog.json
#   In the official Docker image (which this exercise uses) the slow-log
#   appender is a CONSOLE appender, so the lines go to the container's
#   stdout instead -- i.e. you read them with `docker logs`, not by
#   tailing a file. This script auto-detects the Docker case and prints
#   the lines for you; see the SHOW THE SLOW LOG section at the bottom.
#
# These thresholds are applied at the SHARD level: the "query" phase is
# the per-shard search, the "fetch" phase is loading the matched docs.
#
# Pass an index name as the first argument (default: perf_demo) and the
# Elasticsearch container name as the second (default: elasticsearch).
INDEX="${1:-perf_demo}"
CONTAINER="${2:-elasticsearch}"
ES="http://localhost:9200"

echo "=== enabling search + indexing slow logs on '${INDEX}' ==="
curl -s -X PUT "${ES}/${INDEX}/_settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index.search.slowlog.threshold.query.warn": "10s",
	"index.search.slowlog.threshold.query.info": "5s",
	"index.search.slowlog.threshold.query.debug": "2s",
	"index.search.slowlog.threshold.query.trace": "500ms",
	"index.search.slowlog.threshold.fetch.warn": "1s",
	"index.search.slowlog.threshold.fetch.info": "800ms",
	"index.indexing.slowlog.threshold.index.warn": "10s",
	"index.indexing.slowlog.threshold.index.info": "5s",
	"index.indexing.slowlog.threshold.index.debug": "2s",
	"index.indexing.slowlog.threshold.index.trace": "500ms"
}'

# Note: these are DYNAMIC settings, so they take effect immediately with
# no restart. To turn a tier off again, set its threshold to "-1".
echo "=== current slowlog settings on '${INDEX}' ==="
curl -s -X GET \
	"${ES}/${INDEX}/_settings?filter_path=**.slowlog&pretty"

# ---------------------------------------------------------------------------
# DEMO: actually trigger the slow log so you can see real lines.
#
# A query on a tiny demo index finishes in a millisecond or two, far below
# the 500ms trace threshold above, so on an idle laptop NOTHING would ever
# be logged. We use two complementary techniques:
#
#   (1) Drop the trace threshold to 0ms so that ANY query is logged. This
#       guarantees a slow-log line regardless of how fast the box is -- it
#       is the reliable way to see the mechanism work.
#   (2) Also run a GENUINELY expensive query (a leading-wildcard regexp,
#       which cannot use the inverted index and must scan every term).
#       This is the more authentic case: a query that is slow on its own
#       merits. On a fast machine it may still be under 500ms, which is
#       exactly why technique (1) exists as a backstop.
# ---------------------------------------------------------------------------

echo "=== (demo) forcing slow queries on '${INDEX}' ==="

# (1) Log EVERYTHING: set the trace threshold to 0ms for the demo.
curl -s -X PUT "${ES}/${INDEX}/_settings" \
	-H 'Content-Type: application/json' \
	-d'{"index.search.slowlog.threshold.query.trace":"0ms"}' >/dev/null
echo "  - trace threshold temporarily set to 0ms (logs every query)"

# A normal filter + aggregation. Fast, but now guaranteed to be logged.
curl -s "${ES}/${INDEX}/_search?size=0" -H 'Content-Type: application/json' -d'
{
	"query": {"bool": {"filter": [{"term": {"department": "sales"}}]}},
	"aggs": {"by_city": {"terms": {"field": "city"}}}
}' >/dev/null
echo "  - ran a filter + terms aggregation"

# (2) A genuinely expensive query: a leading-wildcard regexp on the
# analyzed text field. The leading ".*" defeats the inverted index and
# forces a full term scan, which is the textbook "why is this slow" query.
curl -s "${ES}/${INDEX}/_search?size=0" -H 'Content-Type: application/json' -d'
{
	"query": {"regexp": {"bio": ".*london.*"}}
}' >/dev/null
echo "  - ran a leading-wildcard regexp (deliberately expensive)"

# Restore the realistic trace threshold now that the demo queries have run.
curl -s -X PUT "${ES}/${INDEX}/_settings" \
	-H 'Content-Type: application/json' \
	-d'{"index.search.slowlog.threshold.query.trace":"500ms"}' >/dev/null
echo "  - trace threshold restored to 500ms"

# Give the async logger a moment to flush the lines.
sleep 1

# ---------------------------------------------------------------------------
# SHOW THE SLOW LOG
#
# In the Docker image the search slow log is a CONSOLE appender, so the
# lines appear on the container's stdout. Pull the most recent search
# slow-log lines out of `docker logs`. (event.dataset is the stable ECS
# field that tags these lines: "elasticsearch.index_search_slowlog".)
# ---------------------------------------------------------------------------
echo "=== recent search slow-log lines (from 'docker logs ${CONTAINER}') ==="
if command -v docker >/dev/null 2>&1 && \
   docker inspect "${CONTAINER}" >/dev/null 2>&1; then
	docker logs "${CONTAINER}" 2>&1 \
		| grep "elasticsearch.index_search_slowlog" \
		| tail -n 5 \
		|| echo "(no slow-log lines found yet -- try re-running)"
else
	echo "container '${CONTAINER}' not found via docker; if you run"
	echo "Elasticsearch from a package install, look instead in the logs"
	echo "directory (e.g. /var/log/elasticsearch/) for the file"
	echo "<cluster>_index_search_slowlog.json"
fi

echo
echo "done. Each line above carries the offending query under"
echo "'elasticsearch.slowlog.source' and its time under"
echo "'elasticsearch.slowlog.took' -- that is how you catch the specific"
echo "requests hurting the cluster. Set a threshold to '-1' to disable a tier."
