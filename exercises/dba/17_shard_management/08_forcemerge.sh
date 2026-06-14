#!/bin/bash -eu
# Force-merge a read-only / no-longer-written index down to one segment.
#
# Every Lucene shard is made of immutable "segments". Indexing and updates
# create many small segments; deletes only mark documents as deleted until a
# merge reclaims the space. Background merges keep this under control, but for
# an index that will NEVER be written again (yesterday's logs, a closed time
# slice) you can proactively merge down to a single segment per shard. This:
#   - reclaims disk from deleted docs,
#   - speeds up searches (fewer segments to scan),
#   - shrinks the heap footprint of segment metadata.
#
# CRITICAL: only force-merge to max_num_segments=1 on indices that are DONE
# being written. A single huge segment on a still-active index can never be
# merged away and will hurt you. So we make the index read-only first.

IDX="logs_shrunk"

# If the shrink step has not been run, fall back to the main index.
if ! curl -s -o /dev/null -w "%{http_code}" "localhost:9200/${IDX}" \
	| grep -q 200; then
	IDX="logs_sharded"
fi
echo "Target index: ${IDX}"

# Segment count BEFORE: expect several segments per shard.
echo "=== segments BEFORE forcemerge ==="
curl -s -X GET \
	"localhost:9200/_cat/segments/${IDX}?v&h=index,shard,prirep,segment,docs.count,size"

# Mark the index read-only: this is the signal that it is finished being
# written, which is the precondition for a safe max_num_segments=1 merge.
echo
echo "=== marking ${IDX} read-only ==="
curl -s -X PUT "localhost:9200/${IDX}/_settings?pretty" \
	-H 'Content-Type: application/json' -d'
{
	"index": {
		"blocks.write": true
	}
}'

# Run the force-merge. This is synchronous and can take a while on big shards
# (it rewrites all the data), so we give curl a generous timeout.
echo
echo "=== force-merging to 1 segment per shard (this can take a while) ==="
curl -s --max-time 300 -X POST \
	"localhost:9200/${IDX}/_forcemerge?max_num_segments=1&pretty"

# Segment count AFTER: expect exactly one segment per shard.
echo
echo "=== segments AFTER forcemerge (expect 1 per shard) ==="
curl -s -X GET \
	"localhost:9200/_cat/segments/${IDX}?v&h=index,shard,prirep,segment,docs.count,size"
