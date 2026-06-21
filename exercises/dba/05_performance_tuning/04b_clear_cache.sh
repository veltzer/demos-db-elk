#!/bin/bash -eu
# Clear Elasticsearch caches for one index (or all indices).
#
# Clearing caches is mostly a DIAGNOSTIC tool: it lets you measure
# cold-cache vs warm-cache behaviour, or reclaim memory after a one-off
# expensive operation. In steady-state you normally let Elasticsearch
# manage these caches itself.
#
# Pass an index name as the first argument, or leave it blank for _all.
INDEX="${1:-_all}"

# Clear every cache type at once.
echo "=== clearing ALL caches for '${INDEX}' ==="
curl -s -X POST "http://localhost:9200/${INDEX}/_cache/clear?pretty"

# You can also clear a single cache type. For example, just the query
# cache (filter bitsets) or just fielddata:
echo "=== clearing only the query cache for '${INDEX}' ==="
curl -s -X POST \
	"http://localhost:9200/${INDEX}/_cache/clear?query=true&pretty"

echo "=== clearing only fielddata for '${INDEX}' ==="
curl -s -X POST \
	"http://localhost:9200/${INDEX}/_cache/clear?fielddata=true&pretty"

# The request cache is controlled per index by a setting. To DISABLE the
# shard request cache for an index (rarely needed):
#   PUT /<index>/_settings { "index.requests.cache.enable": false }
echo "done. Re-run 04_caches.py to watch the caches warm up again."
