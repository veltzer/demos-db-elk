#!/bin/bash -eu
# List and inspect the snapshots in the repository.

REPO="my_fs_repo"

# _all returns full JSON metadata for every snapshot: state, the indices
# it contains, start/end time, duration, shard totals and failures.
echo "=== GET all snapshots (full JSON) ==="
curl -s -X GET "localhost:9200/_snapshot/${REPO}/_all?pretty"

# The _cat API gives a compact one-line-per-snapshot table, which is the
# fastest way for a DBA to eyeball what backups exist and whether they
# succeeded. ?v adds the header row.
echo "=== _cat/snapshots (compact table) ==="
curl -s -X GET "localhost:9200/_cat/snapshots/${REPO}?v&s=start_epoch"

# You can also fetch a single snapshot by name to confirm its contents.
echo "=== GET snap_all metadata ==="
curl -s -X GET "localhost:9200/_snapshot/${REPO}/snap_all?pretty"
