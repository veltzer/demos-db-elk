#!/bin/bash -eu
# Capture hot threads across the cluster.
#
# GET /_nodes/hot_threads samples the busiest threads on every node and
# returns a plain-text report. It is the go-to tool when a node is
# pegged at high CPU and you need to know WHAT it is doing (heavy query,
# merge, GC, script execution, ...).
#
# Useful query parameters:
#   threads=N    - report the top N hottest threads per node (default 3)
#   interval=Ns  - sampling interval (default 500ms)
#   type=cpu     - hot threads by cpu (default), block, wait, or mem
#   snapshots=N  - number of stack snapshots to take (default 10)

echo "=== hot threads (top 3 cpu threads per node) ==="
curl -s -X GET "http://localhost:9200/_nodes/hot_threads"

# A more aggressive capture for a CPU investigation: more threads, a
# longer sampling window, more snapshots so transient work shows up.
echo
echo "=== hot threads (deeper sample) ==="
curl -s -X GET "http://localhost:9200/_nodes/hot_threads?threads=5&interval=1s&snapshots=20&type=cpu"
