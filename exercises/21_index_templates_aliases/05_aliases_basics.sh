#!/bin/bash -eu
# ALIASES basics. An alias is a second name that points at one or more
# indices. Clients talk to the alias; the DBA can repoint the alias to a
# different index later without the client ever changing its config. This
# is the foundation of zero-downtime operations.

# Add a couple of documents to the existing logs-app-2024 index so the
# alias has something to return when queried.
echo "=== index two sample documents ==="
curl -X POST "localhost:9200/logs-app-2024/_doc?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"@timestamp": "2024-01-01T10:00:00Z",
	"level": "INFO",
	"service": "checkout",
	"message": "order placed",
	"status_code": 200,
	"host": "web-01"
}'
curl -X POST "localhost:9200/logs-app-2024/_doc?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"@timestamp": "2024-01-01T10:05:00Z",
	"level": "ERROR",
	"service": "checkout",
	"message": "payment failed",
	"status_code": 500,
	"host": "web-02"
}'

# Make the new docs searchable immediately.
curl -X POST "localhost:9200/logs-app-2024/_refresh?pretty"

# Add an alias "logs-current" pointing at logs-app-2024. The _aliases API
# applies a LIST of actions ATOMICALLY: either all succeed or none do.
# This atomicity is what makes alias swaps safe (see script 07).
echo
echo "=== add alias logs-current -> logs-app-2024 ==="
curl -X POST "localhost:9200/_aliases?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"actions": [
		{ "add": { "index": "logs-app-2024", "alias": "logs-current" } }
	]
}'

# Show all aliases in the cluster.
echo
echo "=== cat aliases ==="
curl -s "localhost:9200/_cat/aliases?v"

# Query THROUGH the alias - exactly as if it were a real index name. The
# request resolves to logs-app-2024 transparently.
echo
echo "=== query through the alias (expect 2 hits) ==="
curl -X GET "localhost:9200/logs-current/_search?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"query": { "match_all": {} }
}'

# Aliases support atomic add AND remove in a single call. Here we move the
# alias from logs-app-2024 to logs-audit-2024 in one transaction, then
# move it back, to demonstrate the pattern.
echo
echo "=== atomically repoint then restore the alias ==="
curl -X POST "localhost:9200/_aliases?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"actions": [
		{ "remove": { "index": "logs-app-2024", "alias": "logs-current" } },
		{ "add": { "index": "logs-audit-2024", "alias": "logs-current" } }
	]
}'
curl -X POST "localhost:9200/_aliases?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"actions": [
		{ "remove": { "index": "logs-audit-2024", "alias": "logs-current" } },
		{ "add": { "index": "logs-app-2024", "alias": "logs-current" } }
	]
}'
