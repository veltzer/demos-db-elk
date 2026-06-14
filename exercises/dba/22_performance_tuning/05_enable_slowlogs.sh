#!/bin/bash -eu
# Turn on the search and indexing SLOW LOGS for one index with sensible
# thresholds.
#
# Slow logs record individual queries / index operations that exceed a
# time threshold, broken into warn/info/debug/trace tiers. They are the
# best way to catch the specific slow requests hurting a cluster, because
# they log the actual query source.
#
# WHERE DO THE LINES LAND?
#   In the dedicated slow-log files in the Elasticsearch logs directory:
#     <index>_index_search_slowlog.json   (and ..._slowlog.log)
#     <index>_index_indexing_slowlog.json (and ..._slowlog.log)
#   On a package install that is usually /var/log/elasticsearch/.
#   In Docker it is inside the container's logs dir (mount it to keep it).
#
# These thresholds are applied at the SHARD level: the "query" phase is
# the per-shard search, the "fetch" phase is loading the matched docs.
#
# Pass an index name as the first argument (default: perf_demo).
INDEX="${1:-perf_demo}"

echo "=== enabling search + indexing slow logs on '${INDEX}' ==="
curl -s -X PUT "http://localhost:9200/${INDEX}/_settings?pretty" \
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
	"http://localhost:9200/${INDEX}/_settings?filter_path=**.slowlog&pretty"

echo "done. Run a slow query, then tail the *_slowlog.json file in the"
echo "Elasticsearch logs directory to see the offending requests."
