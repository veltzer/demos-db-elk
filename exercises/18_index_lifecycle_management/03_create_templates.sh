#!/bin/bash -eu
# Build a composable index template out of reusable component templates.
#
# Modern Elasticsearch (7.8+) splits index templates into:
#   - component templates : reusable fragments of settings / mappings
#   - an index template    : matches index patterns and composes components
#
# Here we create two component templates (settings + mappings) and an index
# template that wires in our ILM policy and the rollover alias. The alias
# ("logs") is what we write to; ILM rolls it onto new backing indices.
#
# Note the literal TABS inside each heredoc JSON body.

# Component template: index settings, including the ILM policy + rollover alias.
curl -X PUT "localhost:9200/_component_template/logs-settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"template": {
		"settings": {
			"number_of_shards": 1,
			"number_of_replicas": 0,
			"index.lifecycle.name": "logs-policy",
			"index.lifecycle.rollover_alias": "logs"
		}
	}
}'

# Component template: field mappings shared by every backing index.
curl -X PUT "localhost:9200/_component_template/logs-mappings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"template": {
		"mappings": {
			"properties": {
				"@timestamp": { "type": "date" },
				"message":    { "type": "text" },
				"level":      { "type": "keyword" },
				"service":    { "type": "keyword" }
			}
		}
	}
}'

# Index template: matches "logs-*" and composes the two components above.
# priority must beat any built-in templates that also match the pattern.
curl -X PUT "localhost:9200/_index_template/logs-template?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index_patterns": ["logs-*"],
	"composed_of": ["logs-settings", "logs-mappings"],
	"priority": 500
}'

echo
echo "Created component templates 'logs-settings', 'logs-mappings' and"
echo "index template 'logs-template' (matches logs-*)."
