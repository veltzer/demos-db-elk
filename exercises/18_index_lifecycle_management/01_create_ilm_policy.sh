#!/bin/bash -eu
# Create an ILM (Index Lifecycle Management) policy named "logs-policy" with
# the classic hot / warm / cold / delete phase model.
#
# Phase summary:
#   hot    - actively written; rolls over on size, age or document count
#   warm   - no longer written; shrink to one shard, force-merge, mark read-only
#   cold   - rarely queried; allocate to cheaper "cold" nodes, read-only
#   delete - removed entirely once retention has elapsed
#
# Note the literal TABS inside the heredoc JSON body.
curl -X PUT "localhost:9200/_ilm/policy/logs-policy?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"policy": {
		"phases": {
			"hot": {
				"min_age": "0ms",
				"actions": {
					"rollover": {
						"max_primary_shard_size": "50gb",
						"max_age": "30d",
						"max_docs": 100000000
					},
					"set_priority": {
						"priority": 100
					}
				}
			},
			"warm": {
				"min_age": "7d",
				"actions": {
					"allocate": {
						"number_of_replicas": 1
					},
					"shrink": {
						"number_of_shards": 1
					},
					"forcemerge": {
						"max_num_segments": 1
					},
					"set_priority": {
						"priority": 50
					}
				}
			},
			"cold": {
				"min_age": "30d",
				"actions": {
					"allocate": {
						"number_of_replicas": 0
					},
					"readonly": {},
					"set_priority": {
						"priority": 0
					}
				}
			},
			"delete": {
				"min_age": "90d",
				"actions": {
					"delete": {}
				}
			}
		}
	}
}'

echo
echo "Created ILM policy 'logs-policy'. Inspect it with:"
echo "  curl -s 'localhost:9200/_ilm/policy/logs-policy?pretty'"
