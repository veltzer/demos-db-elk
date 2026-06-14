#!/bin/bash -eu
# Bootstrap the FIRST backing index for the classic rollover-alias approach.
#
# With a rollover alias you must create the initial index yourself and mark it
# as the write index for the alias. ILM then rolls the alias forward onto
# "logs-000002", "logs-000003", … as the rollover conditions are met.
#
# The index name MUST end in a number (the "-000001" suffix) so that rollover
# can increment it. The "is_write_index": true flag is mandatory.
#
# Note the literal TABS inside the heredoc JSON body.
curl -X PUT "localhost:9200/logs-000001?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"aliases": {
		"logs": {
			"is_write_index": true
		}
	}
}'

echo
echo "Bootstrapped 'logs-000001' as the write index for alias 'logs'."
echo "List the backing indices and which one is the write index:"
echo "  curl -s 'localhost:9200/_cat/indices/logs-*?v'"
echo "  curl -s 'localhost:9200/_alias/logs?pretty'"
