#!/bin/bash -eu
# Generate some syslog entries
now=$(date)
logger "Test message from logstash exercise - ${now}"
logger "Another test message with some data: user=testuser action=login"
logger "Error simulation: failed to connect to database"

# Generate auth log entries (if you have sudo access)
sudo logger -t sshd "Test auth message: authentication failure"
