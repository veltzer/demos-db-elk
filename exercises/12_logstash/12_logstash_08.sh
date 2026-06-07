#!/bin/bash
# Run in background
nohup /opt/logstash/bin/logstash -f simple-logs.conf > logstash.log 2>&1 &

# Check if it's running
ps aux | grep logstash

# View logs
tail -f logstash.log
