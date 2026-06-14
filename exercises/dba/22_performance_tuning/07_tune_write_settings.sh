#!/bin/bash -eu
# Tune an index for a WRITE-HEAVY workload, then show how to restore the
# safe defaults afterwards.
#
# Two dynamic settings dominate write throughput:
#
#   index.refresh_interval
#       How often new docs become searchable. Default 1s. Each refresh
#       creates a new Lucene segment, which costs CPU/IO and produces
#       many small segments to merge later. For bulk loads, raise this
#       (e.g. 30s) or disable it entirely (-1) and refresh manually when
#       done. TRADE-OFF: documents are not searchable until the next
#       refresh, so this hurts near-real-time visibility.
#
#   index.translog.durability
#       "request" (default): the translog is fsync'd to disk on EVERY
#       write request before it is acknowledged -- durable but slower.
#       "async": the translog is fsync'd every sync_interval (default 5s),
#       so a crash can lose up to that window of acknowledged writes, in
#       exchange for higher throughput. Only acceptable when you can
#       re-drive lost writes from the source.
#
# Pass an index name as the first argument (default: perf_demo).
INDEX="${1:-perf_demo}"

echo "=== applying WRITE-HEAVY tuning to '${INDEX}' ==="
curl -s -X PUT "http://localhost:9200/${INDEX}/_settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index.refresh_interval": "30s",
	"index.translog.durability": "async",
	"index.translog.sync_interval": "30s"
}'

echo "=== bulk-load now with the relaxed settings, then force a refresh ==="
echo "    (curl -s -X POST http://localhost:9200/${INDEX}/_refresh)"

# Restoring the safe near-real-time defaults once the bulk load is done.
# Run THIS block (or copy it) after the load to return to normal:
cat <<'EOF'

To RESTORE safe defaults after the load, run:

  curl -s -X PUT "http://localhost:9200/INDEX/_settings?pretty" \
    -H 'Content-Type: application/json' -d'
  {
  	"index.refresh_interval": "1s",
  	"index.translog.durability": "request"
  }'

(replace INDEX with your index name)
EOF

echo "=== current write-related settings on '${INDEX}' ==="
curl -s -X GET \
	"http://localhost:9200/${INDEX}/_settings?filter_path=**.refresh_interval,**.translog&pretty"
