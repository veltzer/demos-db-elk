#!/bin/bash
# Test the configuration syntax
/opt/logstash/bin/logstash --config.test_and_exit -f simple-logs.conf

# Should output "Configuration OK"
