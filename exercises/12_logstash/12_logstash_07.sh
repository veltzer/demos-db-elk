#!/bin/bash
# Run Logstash (this will run in foreground)
/opt/logstash/bin/logstash -f simple-logs.conf

# You should see:
# - Logstash starting up
# - Pipeline being created
# - Log entries being processed (in console output)
# - Data being sent to Elasticsearch
