#!/bin/bash -eu
# No Kibana system user setup is required.
#
# The docker-compose.yml in this exercise runs Elasticsearch with security
# disabled (xpack.security.enabled=false), so there is no kibana_system
# password to generate and no enrollment token to configure. Kibana connects
# to Elasticsearch over plain HTTP with no credentials.
echo "Security is disabled; no Kibana system user setup needed."
