#!/bin/bash -eu
# Inspect nodes and health using the compact _cat APIs.
#
# The _cat APIs return human-friendly tabular text (not JSON) and are
# ideal for a quick terminal glance. Add ?v for a header row, and use
# ?h=col1,col2,... to pick exactly the columns you care about.

# _cat/health gives a one-line cluster summary, optionally with history.
echo "=== _cat/health ==="
curl -s -X GET "http://localhost:9200/_cat/health?v"

# _cat/nodes lists every node with the columns most useful to a DBA:
#   name       - node name
#   node.role  - roles (m=master, d=data, i=ingest, etc.)
#   master     - * marks the elected master
#   heap.percent - JVM heap used % (watch for sustained > 75%)
#   ram.percent  - OS memory used %
#   cpu          - recent CPU %
#   load_1m/5m/15m - OS load averages
echo "=== _cat/nodes (selected columns) ==="
curl -s -X GET "http://localhost:9200/_cat/nodes?v&h=name,node.role,master,heap.percent,ram.percent,cpu,load_1m,load_5m,load_15m,disk.used_percent"

# The full default view shows ip, heap/ram in MB, and more.
echo "=== _cat/nodes (full default view) ==="
curl -s -X GET "http://localhost:9200/_cat/nodes?v"

# _cat/allocation shows shard count and disk usage per node, which is
# essential when chasing disk-watermark allocation problems.
echo "=== _cat/allocation (disk per node) ==="
curl -s -X GET "http://localhost:9200/_cat/allocation?v"
