#!/bin/bash
# Start Kibana in the background
nohup /opt/elastic/kibana/bin/kibana > /tmp/kibana.log 2>&1 &

# Save the PID
echo $! > /tmp/kibana.pid
