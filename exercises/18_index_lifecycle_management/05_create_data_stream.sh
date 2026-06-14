#!/bin/bash -eu
# The MODERN alternative to a rollover alias: a data stream.
#
# A data stream is a named, append-only abstraction over a sequence of hidden
# backing indices (".ds-logs-stream-...-000001", "-000002", …). You never
# create or name the backing indices yourself and you never set is_write_index:
# the data stream always writes to its current backing index and ILM rolls it.
#
# A data stream REQUIRES an index template that contains a "data_stream" object,
# and every document MUST carry an "@timestamp" field.
#
# Note the literal TABS inside each heredoc JSON body.

# Index template enabling a data stream for the "logs-stream*" pattern. It
# reuses the same component templates and ILM policy as the alias approach.
#
# IMPORTANT: this pattern ("logs-stream*") overlaps the rollover-alias template
# from 03_create_templates.sh ("logs-*"). When two templates match a name, the
# one with the higher "priority" wins, so we give this one 600 (vs 500) to make
# sure the data-stream template is the one chosen for "logs-stream".
curl -X PUT "localhost:9200/_index_template/logs-stream-template?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index_patterns": ["logs-stream*"],
	"data_stream": {},
	"composed_of": ["logs-mappings"],
	"template": {
		"settings": {
			"number_of_shards": 1,
			"number_of_replicas": 0,
			"index.lifecycle.name": "logs-policy"
		}
	},
	"priority": 600
}'

# Explicitly create the data stream. (It would also be created implicitly on
# the first index/bulk request that targets the name.) No rollover alias and no
# is_write_index are needed here.
curl -X PUT "localhost:9200/_data_stream/logs-stream?pretty"

echo
echo "Created data stream 'logs-stream'. Inspect it and its backing indices:"
echo "  curl -s 'localhost:9200/_data_stream/logs-stream?pretty'"
echo "  curl -s 'localhost:9200/_cat/indices/.ds-logs-stream*?v'"
