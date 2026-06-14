#!/bin/bash -eu
# Reindex with transformation: a Painless script in the reindex body plus a
# query to copy only a subset of documents.
#
# Three common transform patterns are shown together:
#   1. RENAME a field: copy ctx._source.category into a new field
#      "category_name" and remove the old key.
#   2. DERIVE a field: compute "price_with_tax" from price.
#   3. DROP unwanted docs mid-flight: set ctx.op = "noop" to skip a doc so
#      it is never written to the destination (here we drop price == 0).
#
# The "query" inside source restricts WHICH documents are read - we only
# reindex products in the "Hardware" category. Combine the query and the
# script and you have a powerful one-pass migrate-and-filter.
curl -X DELETE "localhost:9200/products_transformed?pretty" 2>/dev/null || true
curl -X PUT "localhost:9200/products_transformed?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"mappings": {
		"properties": {
			"name":           { "type": "text"    },
			"category_name":  { "type": "keyword" },
			"price":          { "type": "integer" },
			"price_with_tax": { "type": "float"   }
		}
	},
	"settings": {
		"index": {
			"number_of_shards": 1,
			"number_of_replicas": 0
		}
	}
}'

echo
echo "=== reindex with query subset + transform script ==="
curl -X POST "localhost:9200/_reindex?pretty&refresh=true" \
	-H 'Content-Type: application/json' -d'
{
	"source": {
		"index": "products_v1",
		"query": {
			"match": { "category": "Hardware" }
		}
	},
	"dest": { "index": "products_transformed" },
	"script": {
		"lang": "painless",
		"source": "if (ctx._source.price == 0) { ctx.op = '\''noop'\''; } else { ctx._source.category_name = ctx._source.remove('\''category'\''); ctx._source.price_with_tax = ctx._source.price * 1.17; ctx._source.remove('\''created'\''); }"
	}
}'

# Inspect the result. We should see only Hardware docs, with category_name
# (not category), and a computed price_with_tax.
echo
echo "=== transformed documents ==="
curl -s "localhost:9200/products_transformed/_search?pretty"
