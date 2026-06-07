#!/bin/bash
# Start Elasticsearch in the background
/opt/elastic/elasticsearch/bin/elasticsearch -d -p /tmp/elasticsearch.pid

# With security disabled (see the configuration step), no password is
# generated and no credentials are needed to connect.
