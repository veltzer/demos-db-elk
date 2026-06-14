#!/bin/bash -eu
# FILTERED and ROUTING aliases. An alias can carry a query "filter" so it
# only ever exposes a SUBSET of the underlying index, and a "routing" value
# so reads/writes through it are pinned to specific shards. Together these
# give you lightweight, per-tenant or per-severity "views" over one index
# without copying any data.

# (1) FILTERED alias: "logs-errors" exposes only documents where
# level == "ERROR". A search through this alias can never see INFO docs,
# even though they live in the same physical index. Great for handing a
# limited view to a team or dashboard.
echo "=== add filtered alias logs-errors (level == ERROR) ==="
curl -X POST "localhost:9200/_aliases?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"actions": [
		{
			"add": {
				"index": "logs-app-2024",
				"alias": "logs-errors",
				"filter": { "term": { "level": "ERROR" } }
			}
		}
	]
}'

# Query through the filtered alias: expect ONLY the ERROR document, even
# though the index also holds an INFO document.
echo
echo "=== query logs-errors (expect 1 hit, the ERROR doc) ==="
curl -X GET "localhost:9200/logs-errors/_search?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"query": { "match_all": {} }
}'

# (2) ROUTING alias: "logs-checkout" pins both search and index routing to
# the value "checkout". With routing, all documents written through this
# alias land on the same shard, and searches through it only hit that
# shard - a cheap way to co-locate a tenant's data. (With a single shard
# the effect is hard to observe, but the configuration is identical at any
# shard count.)
echo
echo "=== add routing alias logs-checkout (routing=checkout) ==="
curl -X POST "localhost:9200/_aliases?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"actions": [
		{
			"add": {
				"index": "logs-app-2024",
				"alias": "logs-checkout",
				"routing": "checkout"
			}
		}
	]
}'

# Index a document through the routing alias - it inherits routing=checkout.
echo
echo "=== write through the routing alias ==="
curl -X POST "localhost:9200/logs-checkout/_doc?refresh=true&pretty" \
	-H 'Content-Type: application/json' -d'
{
	"@timestamp": "2024-01-01T10:10:00Z",
	"level": "INFO",
	"service": "checkout",
	"message": "cart updated",
	"status_code": 200,
	"host": "web-03"
}'

# Show the alias metadata, including the stored filter and routing.
echo
echo "=== alias definitions on logs-app-2024 ==="
curl -s "localhost:9200/logs-app-2024/_alias?pretty"
