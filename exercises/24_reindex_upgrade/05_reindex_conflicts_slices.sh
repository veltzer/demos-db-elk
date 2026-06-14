#!/bin/bash -eu
# Handling conflicts and parallelising large reindexes.
#
# CONFLICTS: by default reindex uses op_type "index", which overwrites docs
# in the destination. If the destination already contains a document with
# the same _id AND you set op_type=create, a version conflict is raised and
# the whole reindex ABORTS. Setting "conflicts": "proceed" tells reindex to
# count the conflict, skip that doc, and keep going instead of failing.
#
# SLICES: a single reindex is single-threaded per shard. "slices": "auto"
# (or a fixed integer) splits the source into N parallel sub-tasks, one per
# shard, so the copy uses all the cores. This is the main lever for making
# a multi-million-doc reindex finish in a reasonable time.
#
# REQUESTS_PER_SECOND: the throttle. It caps the indexing rate so a giant
# reindex does not saturate the cluster and starve live traffic. Set to -1
# for unlimited, or a number like 2000 to keep headroom for production.
#
# First pre-populate the destination with ONE doc that has a known _id so we
# can demonstrate a conflict against op_type=create.
curl -X DELETE "localhost:9200/products_conflict?pretty" 2>/dev/null || true
curl -X PUT "localhost:9200/products_conflict/_doc/fixed-1?refresh=true&pretty" \
	-H 'Content-Type: application/json' -d'
{ "name": "Pre-existing", "category": "Hardware", "price": 1 }'

# Source index whose docs include one with the SAME _id (fixed-1). When we
# reindex with op_type=create that single doc collides.
curl -X DELETE "localhost:9200/products_src?pretty" 2>/dev/null || true
curl -X POST "localhost:9200/products_src/_bulk?refresh=true" \
	-H 'Content-Type: application/json' -d'
{ "index": { "_id": "fixed-1" } }
{ "name": "Clash",  "category": "Hardware", "price": 5 }
{ "index": { "_id": "new-2" } }
{ "name": "Fresh",  "category": "Hardware", "price": 6 }
{ "index": { "_id": "new-3" } }
{ "name": "Fresh2", "category": "Hardware", "price": 7 }
'

# Reindex with op_type=create + conflicts=proceed + parallel slices + a
# throttle. The fixed-1 doc conflicts and is skipped (reported under
# "version_conflicts"); the other two are created.
echo
echo "=== reindex: conflicts=proceed, slices=auto, throttled ==="
curl -X POST \
	"localhost:9200/_reindex?pretty&refresh=true&requests_per_second=2000&slices=auto" \
	-H 'Content-Type: application/json' -d'
{
	"conflicts": "proceed",
	"source": { "index": "products_src" },
	"dest":   { "index": "products_conflict", "op_type": "create" }
}'

# Expect: created=2, version_conflicts=1, total=3. The pre-existing doc was
# left untouched because of op_type=create + conflicts=proceed.
echo
echo "=== resulting count (should be 3: 1 original + 2 created) ==="
curl -s "localhost:9200/_cat/count/products_conflict?v"

# You can also re-throttle a RUNNING reindex without restarting it via the
# Tasks API (rethrottle), e.g.:
#   POST /_reindex/<task_id>/_rethrottle?requests_per_second=500
echo
echo "(throttle a running reindex live: POST /_reindex/<id>/_rethrottle?requests_per_second=N)"
