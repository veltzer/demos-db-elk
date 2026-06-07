#!/bin/bash
# Generate password for kibana_system user
docker exec -it elasticsearch /usr/share/elasticsearch/bin/elasticsearch-reset-password \
-u kibana_system -b

# Update the ELASTICSEARCH_PASSWORD in docker-compose.yml with the new password
# Then restart Kibana
docker compose restart kibana
