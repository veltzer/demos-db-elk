#!/bin/bash -eu
# Run in background
nohup /opt/logstash/bin/logstash -f simple-logs.conf > logstash.log 2>&1 &

# Check if it's running (|| true so a no-match grep doesn't abort under -e)
pgrep -a logstash || true

# View logs
tail -f logstash.log
