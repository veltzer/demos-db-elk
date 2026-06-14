#!/bin/bash -eu
# Reindex to change a field's type - the canonical reason reindex exists.
#
# You CANNOT change the type of an existing field in place. Once "created"
# was mapped as text in products_v1, Elasticsearch will refuse to remap it
# to date on that index. The only supported fix is:
#   1. create a NEW index with the corrected mapping, then
#   2. reindex the old data into it.
#
# Here we promote "created" from text to a real "date" and "price" stays an
# integer. Because the source values like "2024-01-15" are valid ISO dates,
# Elasticsearch parses them into the date field automatically during copy.
#
# Step 1: create products_v2 with the FIXED mapping up front.
curl -X DELETE "localhost:9200/products_v2?pretty" 2>/dev/null || true
curl -X PUT "localhost:9200/products_v2?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"mappings": {
		"properties": {
			"name":     { "type": "text"    },
			"category": { "type": "keyword" },
			"price":    { "type": "integer" },
			"created":  { "type": "date"    }
		}
	},
	"settings": {
		"index": {
			"number_of_shards": 1,
			"number_of_replicas": 0
		}
	}
}'

# Step 2: reindex products_v1 -> products_v2. The destination mapping wins:
# "created" is stored as a date and "category" as a keyword.
echo
echo "=== reindex into corrected mapping ==="
curl -X POST "localhost:9200/_reindex?pretty&refresh=true" \
	-H 'Content-Type: application/json' -d'
{
	"source": { "index": "products_v1" },
	"dest":   { "index": "products_v2"  }
}'

# Prove the type really changed: a date range query only works against a
# date field. If "created" were still text this query would error or behave
# as a string comparison.
echo
echo "=== date range query (only possible with a real date field) ==="
curl -s "localhost:9200/products_v2/_search?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"query": {
		"range": {
			"created": { "gte": "2024-02-01", "lte": "2024-03-31" }
		}
	}
}'

# Show the destination mapping to confirm the new field types.
echo
echo "=== products_v2 mapping ==="
curl -s "localhost:9200/products_v2/_mapping?pretty"
