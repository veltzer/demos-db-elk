#!/bin/bash -eu
# Create two small sample indices with data so we have something to back up.
#
# We deliberately create TWO indices so later steps can demonstrate
# selective (per-index) snapshots and selective restores.

# --- index "customers" -------------------------------------------------
echo "=== create index customers ==="
curl -s -X PUT "localhost:9200/customers?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"settings": {
		"number_of_shards": 1,
		"number_of_replicas": 0
	},
	"mappings": {
		"properties": {
			"name": { "type": "keyword" },
			"city": { "type": "keyword" }
		}
	}
}'

echo "=== bulk load customers ==="
curl -s -X POST "localhost:9200/_bulk?pretty" \
	-H 'Content-Type: application/x-ndjson' --data-binary '
{ "index": { "_index": "customers", "_id": "1" } }
{ "name": "Alice", "city": "Tel Aviv" }
{ "index": { "_index": "customers", "_id": "2" } }
{ "name": "Bob", "city": "Haifa" }
{ "index": { "_index": "customers", "_id": "3" } }
{ "name": "Carol", "city": "Jerusalem" }
'

# --- index "orders" ----------------------------------------------------
echo "=== create index orders ==="
curl -s -X PUT "localhost:9200/orders?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"settings": {
		"number_of_shards": 1,
		"number_of_replicas": 0
	},
	"mappings": {
		"properties": {
			"customer": { "type": "keyword" },
			"amount": { "type": "float" }
		}
	}
}'

echo "=== bulk load orders ==="
curl -s -X POST "localhost:9200/_bulk?pretty" \
	-H 'Content-Type: application/x-ndjson' --data-binary '
{ "index": { "_index": "orders", "_id": "1" } }
{ "customer": "Alice", "amount": 19.99 }
{ "index": { "_index": "orders", "_id": "2" } }
{ "customer": "Bob", "amount": 42.50 }
{ "index": { "_index": "orders", "_id": "3" } }
{ "customer": "Alice", "amount": 7.25 }
{ "index": { "_index": "orders", "_id": "4" } }
{ "customer": "Carol", "amount": 99.00 }
'

# Show the resulting document counts.
echo "=== document counts ==="
curl -s -X GET "localhost:9200/_cat/count/customers?v"
curl -s -X GET "localhost:9200/_cat/count/orders?v"
