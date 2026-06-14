#!/bin/bash -eu
# Basic _reindex: copy every document from a source index into a brand new
# destination index. This is the simplest reindex there is - no mapping
# change, no transformation, just a server-side copy.
#
# We first build a small "products_v1" source index and load a few docs so
# the rest of this exercise has something to work with.
curl -X DELETE "localhost:9200/products_v1?pretty" 2>/dev/null || true
curl -X PUT "localhost:9200/products_v1?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"mappings": {
		"properties": {
			"name":     { "type": "text" },
			"category": { "type": "text" },
			"price":    { "type": "integer" },
			"created":  { "type": "text" }
		}
	},
	"settings": {
		"index": {
			"number_of_shards": 1,
			"number_of_replicas": 0
		}
	}
}'

# Load four documents with the bulk API. Note "created" is a string that we
# will later want to be a real date - that motivates the mapping-change
# reindex in 02_reindex_mapping_change.sh.
curl -X POST "localhost:9200/products_v1/_bulk?refresh=true" \
	-H 'Content-Type: application/json' -d'
{ "index": {} }
{ "name": "Widget",  "category": "Hardware", "price": 10, "created": "2024-01-15" }
{ "index": {} }
{ "name": "Gadget",  "category": "Hardware", "price": 25, "created": "2024-02-20" }
{ "index": {} }
{ "name": "Manual",  "category": "Docs",     "price": 0,  "created": "2024-03-05" }
{ "index": {} }
{ "name": "Service", "category": "Support",  "price": 99, "created": "2024-04-10" }
'

# Drop any previous destination so this script is re-runnable.
curl -X DELETE "localhost:9200/products_v1_copy?pretty" 2>/dev/null || true

# The reindex itself. With wait_for_completion=true (the default) the call
# blocks until the copy is finished and returns a summary: how many docs
# were created, how long it took, and whether there were failures.
echo
echo "=== reindex products_v1 -> products_v1_copy ==="
curl -X POST "localhost:9200/_reindex?pretty&refresh=true" \
	-H 'Content-Type: application/json' -d'
{
	"source": { "index": "products_v1" },
	"dest":   { "index": "products_v1_copy" }
}'

# Confirm both indices hold the same number of documents.
echo
echo "=== document counts ==="
curl -s "localhost:9200/_cat/count/products_v1?v"
curl -s "localhost:9200/_cat/count/products_v1_copy?v"
