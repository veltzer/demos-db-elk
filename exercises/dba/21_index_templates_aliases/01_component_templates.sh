#!/bin/bash -eu
# Create two reusable COMPONENT templates.
#
# A component template is a named, standalone bundle of settings and/or
# mappings. It does nothing on its own: it only takes effect when a
# composable index template references it via "composed_of". This lets a
# DBA define a piece once (for example a standard shard/replica policy)
# and reuse it across many index templates.
#
# Component 1: "common-settings" - shared index settings every index in
# the estate should inherit (shards, replicas, refresh interval).
curl -X PUT "localhost:9200/_component_template/common-settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"template": {
		"settings": {
			"index": {
				"number_of_shards": 1,
				"number_of_replicas": 0,
				"refresh_interval": "5s"
			}
		}
	},
	"_meta": {
		"description": "Shared settings: 1 shard, 0 replicas, 5s refresh",
		"owner": "dba-team"
	}
}'

# Component 2: "logs-mappings" - the field mappings shared by every log
# index. Note we use date/keyword/text types appropriate for log data.
curl -X PUT "localhost:9200/_component_template/logs-mappings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"template": {
		"mappings": {
			"properties": {
				"@timestamp": { "type": "date" },
				"level": { "type": "keyword" },
				"service": { "type": "keyword" },
				"message": { "type": "text" },
				"status_code": { "type": "integer" }
			}
		}
	},
	"_meta": {
		"description": "Common log fields shared across all log indices",
		"owner": "dba-team"
	}
}'

# List the component templates we just created.
echo
echo "=== component templates ==="
curl -s "localhost:9200/_cat/component_templates?v"
