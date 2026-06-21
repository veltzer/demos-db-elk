#!/bin/bash -eu
# Create several SEPARATE physical indices that we will later hide behind a
# single alias. The whole point of this exercise is that the application
# never learns these names exist - it will only ever talk to one stable
# alias. Here we partition log data by month, the classic time-series
# layout: one index per month keeps each index small and lets us drop a
# whole month by deleting one index.

# We create three monthly indices plus one "current" index that will be the
# write target. Each is an ordinary index; nothing special marks them as
# belonging to an alias yet. That association is added in script 02.
echo "=== creating monthly indices ==="
for month in 2026.04 2026.05 2026.06; do
	curl -X PUT "localhost:9200/logs-${month}?pretty" \
		-H 'Content-Type: application/json' -d'
	{
		"settings": {
			"number_of_shards": 1,
			"number_of_replicas": 0
		},
		"mappings": {
			"properties": {
				"@timestamp": { "type": "date" },
				"level":      { "type": "keyword" },
				"service":    { "type": "keyword" },
				"message":    { "type": "text" }
			}
		}
	}'
	echo
done

# Index a few documents into each month so the fan-out query later has
# something to return from every index. Note we write to the CONCRETE index
# names here only to seed historical data; in steady state the application
# writes through the alias instead (see script 02).
echo "=== seeding one document per month ==="
curl -X POST "localhost:9200/logs-2026.04/_doc?pretty" \
	-H 'Content-Type: application/json' -d'
{ "@timestamp": "2026-04-15T08:00:00Z", "level": "INFO", "service": "api", "message": "april request" }'
curl -X POST "localhost:9200/logs-2026.05/_doc?pretty" \
	-H 'Content-Type: application/json' -d'
{ "@timestamp": "2026-05-15T08:00:00Z", "level": "WARN", "service": "api", "message": "may slow query" }'
curl -X POST "localhost:9200/logs-2026.06/_doc?pretty" \
	-H 'Content-Type: application/json' -d'
{ "@timestamp": "2026-06-15T08:00:00Z", "level": "ERROR", "service": "api", "message": "june failure" }'

# Make the seeded documents searchable immediately.
echo
echo "=== refresh ==="
curl -X POST "localhost:9200/logs-2026.04,logs-2026.05,logs-2026.06/_refresh?pretty"

echo
echo "=== the indices we just created (all separate, no alias yet) ==="
curl -s "localhost:9200/_cat/indices/logs-2026.*?v&s=index"
