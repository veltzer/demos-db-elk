#!/bin/bash
# Start Elasticsearch in the background
/opt/elastic/elasticsearch/bin/elasticsearch -d -p /tmp/elasticsearch.pid

# Note the generated password for elastic user in the output!
# If you need to reset it:
/opt/elastic/elasticsearch/bin/elasticsearch-reset-password -u elastic
