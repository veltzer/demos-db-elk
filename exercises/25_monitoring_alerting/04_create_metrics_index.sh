#!/bin/bash -eu
# Create an index template for the self-monitoring metrics index.
#
# We index our collected metrics back into Elasticsearch under names like
# dba-metrics-000001 so they can be charted in Kibana over time. A matching
# index template ensures every dba-metrics-* index gets the right field
# types (especially @timestamp as a date) no matter who creates it.
#
# We use a rollover-friendly template + an initial index with a write alias
# (dba-metrics) so the self-monitoring writer never has to know the concrete
# index name. This is the same pattern Beats and data streams use under the
# hood. (You could also use a real data stream; see exercise 21 for templates
# and aliases, and exercise 18 for ILM-driven rollover.)

# 1. Index template applied to every dba-metrics-* index.
curl -X PUT "localhost:9200/_index_template/dba-metrics?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index_patterns": ["dba-metrics-*"],
	"template": {
		"settings": {
			"number_of_shards": 1,
			"number_of_replicas": 0
		},
		"mappings": {
			"properties": {
				"@timestamp":                    { "type": "date" },
				"cluster_name":                  { "type": "keyword" },
				"status":                        { "type": "keyword" },
				"number_of_nodes":               { "type": "integer" },
				"number_of_data_nodes":          { "type": "integer" },
				"active_primary_shards":         { "type": "integer" },
				"active_shards":                 { "type": "integer" },
				"relocating_shards":             { "type": "integer" },
				"initializing_shards":           { "type": "integer" },
				"unassigned_shards":             { "type": "integer" },
				"pending_tasks":                 { "type": "integer" },
				"active_shards_percent":         { "type": "float" },
				"heap_used_percent_max":         { "type": "float" },
				"gc_collection_time_ms_total":   { "type": "long" },
				"thread_pool_rejections_total":  { "type": "long" },
				"disk_used_percent_max":         { "type": "float" },
				"index_count":                   { "type": "integer" },
				"total_store_bytes":             { "type": "long" },
				"total_store_gb":                { "type": "float" }
			}
		}
	}
}'

# 2. Initial backing index with the dba-metrics write alias. The writer
#    targets the alias; rollover (if you set up ILM) creates -000002, etc.
curl -X PUT "localhost:9200/dba-metrics-000001?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"aliases": {
		"dba-metrics": {
			"is_write_index": true
		}
	}
}'

echo
echo "Created index template 'dba-metrics' and index 'dba-metrics-000001'."
echo "Write to the 'dba-metrics' alias from the self-monitoring scripts."
