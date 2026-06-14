#!/bin/bash -eu
# Create a COMPOSABLE INDEX template (the modern replacement for the
# deprecated legacy "_template" API). A composable index template ties
# together one or more component templates and applies to any index whose
# name matches "index_patterns".
#
# Key fields:
#   index_patterns - which new index names this template applies to.
#   composed_of    - the component templates to merge, in order. Later
#                    components win on conflicts.
#   template       - inline overrides applied AFTER the components, so the
#                    template block has the highest precedence of all.
#   priority       - when several index templates match the same name, the
#                    one with the HIGHEST priority wins (only one applies).
#
# This template covers any index named "logs-*". We use priority 150 (not a
# round 100) on purpose: a stack-managed template named "logs" ships with
# x-pack/Kibana using the pattern "logs-*-*" at priority 100. Elasticsearch
# refuses to register two templates whose patterns can overlap at the SAME
# priority, so "logs-*" at 100 would be rejected. 150 sidesteps that clash
# while still sitting BELOW the audit template (200) so precedence holds.
curl -X PUT "localhost:9200/_index_template/logs-template?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index_patterns": ["logs-*"],
	"composed_of": ["common-settings", "logs-fields"],
	"priority": 150,
	"template": {
		"settings": {
			"index": {
				"number_of_replicas": 1
			}
		},
		"mappings": {
			"properties": {
				"host": { "type": "keyword" }
			}
		}
	},
	"_meta": {
		"description": "Composable template for all logs-* indices"
	}
}'

# A SECOND, more specific template demonstrating PRECEDENCE. It matches the
# narrower pattern "logs-audit-*" and uses a HIGHER priority (200). For an
# index named "logs-audit-2024", BOTH templates match by pattern, but only
# the higher-priority one is applied. It bumps replicas to 2 and adds an
# audit-specific field.
curl -X PUT "localhost:9200/_index_template/logs-audit-template?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index_patterns": ["logs-audit-*"],
	"composed_of": ["common-settings", "logs-fields"],
	"priority": 200,
	"template": {
		"settings": {
			"index": {
				"number_of_replicas": 2
			}
		},
		"mappings": {
			"properties": {
				"actor": { "type": "keyword" },
				"action": { "type": "keyword" }
			}
		}
	},
	"_meta": {
		"description": "Higher-priority template for audit logs"
	}
}'

# List index templates and their priorities.
echo
echo "=== index templates ==="
curl -s "localhost:9200/_cat/templates?v&h=name,index_patterns,composed_of,order"
