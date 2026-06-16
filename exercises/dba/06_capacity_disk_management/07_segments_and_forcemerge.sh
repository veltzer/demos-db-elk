#!/bin/bash -eu
# Segments are the immutable Lucene files that make up a shard. Every refresh
# can create a new segment; ES merges them in the background. Too many small
# segments waste disk and RAM and slow search. A DBA inspects segments to
# decide whether a forcemerge is worthwhile (typically on read-only/old
# indices, e.g. yesterday's time-based index).

# _cat/segments: one row per segment per shard. Key columns:
#   segment   - segment name
#   docs.count- live documents in the segment
#   docs.deleted - deleted docs still occupying disk until merged away
#   size      - on-disk size of the segment
#   committed - whether it has been fsynced
# Lots of rows with high docs.deleted means a forcemerge would reclaim space.
echo "=== segments for capacity_demo ==="
curl -s -X GET \
	"localhost:9200/capacity_demo/_segments?pretty" | head -60

echo
echo "=== compact segment view (_cat/segments) ==="
curl -s -X GET \
	"localhost:9200/_cat/segments/capacity_demo?v&h=index,shard,prirep,segment,docs.count,docs.deleted,size,size.memory"

# Count segments per shard - the number you want to shrink with forcemerge.
echo
echo "=== segment count per shard ==="
curl -s -X GET "localhost:9200/_cat/segments/capacity_demo?h=shard,prirep" \
	| sort | uniq -c

# forcemerge down to a single segment per shard. ONLY do this on indices that
# are no longer being written to: merging a hot index wastes I/O because new
# segments keep appearing. max_num_segments=1 gives the smallest, fastest index
# but is heavy; this can take a while and a lot of I/O on large indices.
echo
echo "=== forcemerge to 1 segment per shard (do this on COLD indices only) ==="
curl -s -X POST \
	"localhost:9200/capacity_demo/_forcemerge?max_num_segments=1&pretty"

# Re-check the segment count; you should now see 1 segment per shard.
echo
echo "=== segment count after forcemerge ==="
curl -s -X GET "localhost:9200/_cat/segments/capacity_demo?h=shard,prirep" \
	| sort | uniq -c
