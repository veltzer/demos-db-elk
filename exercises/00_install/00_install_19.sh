#!/bin/bash
# Edit configuration
nano /opt/elastic/elasticsearch/config/elasticsearch.yml

# Add/modify these lines:
# network.host: 0.0.0.0
# http.port: 9200
# discovery.type: single-node

# Set JVM heap size (optional)
nano /opt/elastic/elasticsearch/config/jvm.options
# Modify -Xms1g and -Xmx1g based on your system
