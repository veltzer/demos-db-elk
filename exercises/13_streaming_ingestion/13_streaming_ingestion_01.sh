#!/bin/bash -eu
# Create the "wpt" (web page timings) index with an explicit mapping so the
# streamed fields are typed correctly from the first document onward.
curl -X PUT "localhost:9200/wpt?pretty" -H 'Content-Type: application/json' -d'
{
	"mappings": {
		"properties": {
			"day": { "type": "integer" },
			"speed_of_load": { "type": "float" }
		}
	},
	"settings": {
		"index": {
			"number_of_shards": 1,
			"number_of_replicas": 0
		}
	}
}'
