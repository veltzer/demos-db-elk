#!/bin/bash -eu
# Edit configuration
nano /opt/elastic/elasticsearch/config/elasticsearch.yml

# Add/modify these lines (security is DISABLED for these exercises):
# network.host: 0.0.0.0
# http.port: 9200
# discovery.type: single-node
# xpack.security.enabled: false
# xpack.security.enrollment.enabled: false
# xpack.security.http.ssl.enabled: false
# xpack.security.transport.ssl.enabled: false

# Set JVM heap size (optional)
nano /opt/elastic/elasticsearch/config/jvm.options
# Modify -Xms1g and -Xmx1g based on your system
