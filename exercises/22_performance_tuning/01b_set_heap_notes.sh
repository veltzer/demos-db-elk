#!/bin/bash -eu
# How to SET the JVM heap size for Elasticsearch (documented, not destructive).
#
# This script does NOT change your running cluster. It prints the two
# supported ways to set heap and inspects what your node is currently
# using, so you can compare against the rules of thumb.
#
# RULES OF THUMB
#   * heap <= 50% of physical RAM  (the rest feeds the OS file cache)
#   * heap < ~31GB                 (so the JVM keeps compressed oops)
#   * set Xms == Xmx               (avoid the JVM resizing the heap)
#
# METHOD 1 (preferred): a jvm.options.d drop-in file.
#   Create /etc/elasticsearch/jvm.options.d/heap.options containing:
#       -Xms8g
#       -Xmx8g
#   Drop-in files survive package upgrades; do NOT edit the main
#   jvm.options file directly.
#
# METHOD 2: the ES_JAVA_OPTS environment variable (handy for Docker).
#   export ES_JAVA_OPTS="-Xms8g -Xmx8g"
#   In docker-compose this is just an environment entry on the service.
#
# Either way you MUST restart the node for the new heap to take effect.
echo "=== current max heap reported by the running node(s) ==="
curl -s -X GET \
	"http://localhost:9200/_nodes/stats/jvm?filter_path=nodes.*.name,nodes.*.jvm.mem.heap_max_in_bytes&pretty"

echo "=== JVM args the node was started with (look for -Xmx / -Xms) ==="
curl -s -X GET \
	"http://localhost:9200/_nodes/jvm?filter_path=nodes.*.name,nodes.*.jvm.input_arguments&pretty"
