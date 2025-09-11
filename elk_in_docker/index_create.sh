#!/bin/bash -eu
curl -X PUT "localhost:9200/wpt?pretty" -H 'Content-Type: application/json' -d'
{
	"settings": {
		"index": {
			"number_of_shards": 1,
			"number_of_replicas": 1
		}
	}
}'
