#!/usr/bin/env python
"""Automated disaster-recovery drill.

A DR drill proves that a backup is actually restorable. Taking snapshots
is worthless if you have never verified that a restore brings the data
back intact. This script runs the full loop against a throwaway index:

    1. create an index and load known data
    2. record the document count
    3. take a snapshot of that index
    4. DELETE the index (simulate disaster)
    5. restore it from the snapshot
    6. compare the restored document count to the original
    7. print PASS or FAIL

Run it on a schedule (for example weekly) so a broken backup is caught
long before you actually need it.

PREREQUISITE: a filesystem repository requires path.repo to be set on the
node (see exercise.md). This script registers the repository for you, but
the path.repo node setting and restart must already be in place.
"""

import sys
import time
from typing import Any

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

REPO = "my_fs_repo"
INDEX = "dr_drill_index"
SNAPSHOT = "dr_drill_snapshot"
DOC_COUNT = 500


def ensure_repository() -> None:
    """Register the filesystem repository (idempotent)."""
    print(f"[1] ensuring repository {REPO!r} exists ...")
    es.snapshot.create_repository(
        name=REPO,
        body={
            "type": "fs",
            "settings": {"location": "backups", "compress": True},
        },
    )


def load_known_data() -> int:
    """Recreate the drill index and load DOC_COUNT documents.

    Returns the document count actually present after a refresh.
    """
    print(f"[2] loading {DOC_COUNT} documents into {INDEX!r} ...")
    es.options(ignore_status=404).indices.delete(index=INDEX)
    es.indices.create(
        index=INDEX,
        body={
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
            },
            "mappings": {
                "properties": {
                    "value": {"type": "integer"},
                    "label": {"type": "keyword"},
                }
            },
        },
    )

    operations: list[dict[str, Any]] = []
    for i in range(DOC_COUNT):
        operations.append({"index": {"_index": INDEX, "_id": str(i)}})
        operations.append({"value": i, "label": f"row-{i}"})
    es.bulk(operations=operations, refresh=True)

    count = es.count(index=INDEX)["count"]
    print(f"    loaded count = {count}")
    return count


def take_snapshot() -> None:
    """Take a blocking snapshot of just the drill index."""
    print(f"[3] taking snapshot {SNAPSHOT!r} ...")
    # Delete any leftover snapshot from a previous run so the name is free.
    es.options(ignore_status=404).snapshot.delete(
        repository=REPO, snapshot=SNAPSHOT
    )
    es.snapshot.create(
        repository=REPO,
        snapshot=SNAPSHOT,
        body={"indices": INDEX, "include_global_state": False},
        wait_for_completion=True,
    )


def simulate_disaster() -> None:
    """Delete the index to simulate catastrophic data loss."""
    print(f"[4] deleting {INDEX!r} to simulate disaster ...")
    es.indices.delete(index=INDEX)
    # Confirm it is really gone.
    assert not es.indices.exists(index=INDEX), "index should be gone"


def restore() -> None:
    """Restore the drill index from the snapshot and wait for green."""
    print(f"[5] restoring {INDEX!r} from snapshot ...")
    es.snapshot.restore(
        repository=REPO,
        snapshot=SNAPSHOT,
        body={"indices": INDEX, "include_global_state": False},
        wait_for_completion=True,
    )
    # The restore call returns once shards are recovering; wait until the
    # index is actually searchable before counting.
    es.cluster.health(index=INDEX, wait_for_status="yellow", timeout="30s")
    es.indices.refresh(index=INDEX)


def verify(expected: int) -> bool:
    """Compare the restored count to the expected count."""
    print("[6] verifying restored document count ...")
    actual = es.count(index=INDEX)["count"]
    print(f"    expected = {expected}, restored = {actual}")
    return actual == expected


def cleanup() -> None:
    """Remove the throwaway index and snapshot left by the drill."""
    print("[7] cleaning up drill artifacts ...")
    es.options(ignore_status=404).indices.delete(index=INDEX)
    es.options(ignore_status=404).snapshot.delete(
        repository=REPO, snapshot=SNAPSHOT
    )


def main() -> int:
    """Run the DR drill and return a process exit code."""
    start = time.perf_counter()
    ensure_repository()
    expected = load_known_data()
    take_snapshot()
    simulate_disaster()
    restore()
    passed = verify(expected)
    cleanup()

    elapsed = time.perf_counter() - start
    print("-" * 60)
    if passed:
        print(f"RESULT: PASS  (drill completed in {elapsed:.1f}s)")
        return 0
    print(f"RESULT: FAIL  (drill completed in {elapsed:.1f}s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
