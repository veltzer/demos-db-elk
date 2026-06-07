#!/bin/bash
# Terminal 1: System logs
/opt/logstash/bin/logstash -f simple-logs.conf

# Terminal 2: Web logs (if available)
/opt/logstash/bin/logstash -f web-logs.conf
