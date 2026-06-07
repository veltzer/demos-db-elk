#!/bin/bash
# Stop Logstash (Ctrl+C if running in foreground)
# Or kill background process:
pkill -f logstash

# Remove test indices
curl -X DELETE "localhost:9200/system-logs-*"
curl -X DELETE "localhost:9200/web-logs-*"
