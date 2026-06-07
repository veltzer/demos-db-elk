#!/bin/bash -eu
# Create the "articles" index with a dense_vector field for kNN search.
#
# - "embedding" is the vector field. dims must match embedding.py (16).
#   index:true + similarity:cosine builds an HNSW graph for approximate kNN.
# - "title"/"content" stay as normal text so we can also do BM25 (lexical)
#   search and combine the two into a hybrid query.
# - "category" is a keyword so we can filter kNN results.
curl -X PUT "localhost:9200/articles?pretty" -H 'Content-Type: application/json' -d'
{
	"mappings": {
		"properties": {
			"title":    { "type": "text" },
			"content":  { "type": "text" },
			"category": { "type": "keyword" },
			"embedding": {
				"type": "dense_vector",
				"dims": 16,
				"index": true,
				"similarity": "cosine"
			}
		}
	},
	"settings": {
		"index": {
			"number_of_shards": 1,
			"number_of_replicas": 0
		}
	}
}'
