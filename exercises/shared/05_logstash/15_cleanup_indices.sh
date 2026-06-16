#!/bin/bash -eu
# Stop Logstash (Ctrl+C if running in foreground)
# Or kill background process. Match the binary path, not just "logstash":
# a bare "logstash" pattern also matches this script's own command line
# (the directory is named 12_logstash) and kills it before the curls run.
# "|| true" so the script continues when Logstash is not running.
pkill -f /opt/logstash || true

# Remove test indices. Elasticsearch 8+ rejects wildcard DELETE by default
# (action.destructive_requires_name), so resolve the names first.
for idx in $(curl -s "localhost:9200/_cat/indices/system-logs-*,web-logs-*?h=index"); do
    curl -X DELETE "localhost:9200/${idx}"
    echo
done
