#!/usr/bin/env python
"""Zero-downtime mapping change via the classic alias-swap pattern.

The problem: you cannot change the type of an existing field in place. To
"change a mapping" you must build a NEW index with the new mapping and move
the data across. Done naively (delete + recreate) there is a window where
the index does not exist and clients fail.

The solution: never let clients talk to a concrete index. Give them two
aliases instead:

    app-write  -> the index that currently accepts writes
    app-read   -> the index(es) that currently serve reads

To roll out a new mapping:

    1. Create v2 with the new mapping.
    2. _reindex v1 -> v2 (v1 still serves reads the whole time).
    3. In ONE atomic _aliases call, repoint app-read from v1 to v2 (and
       app-write too). Because remove+add happen together, there is never a
       moment where the alias points at zero indices.
    4. Optionally drop v1.

This script performs the whole dance and verifies document counts before
and after the swap so you can prove no documents were lost.
"""

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

V1 = "app-000001"
V2 = "app-000002"
WRITE_ALIAS = "app-write"
READ_ALIAS = "app-read"


def cleanup_previous() -> None:
    """Remove anything left over from a prior run so the demo is repeatable."""
    for index in (V1, V2):
        if es.indices.exists(index=index):
            es.indices.delete(index=index)


def create_v1() -> None:
    """Create v1 with the OLD mapping (status_code as a keyword)."""
    es.indices.create(
        index=V1,
        mappings={
            "properties": {
                "@timestamp": {"type": "date"},
                "service": {"type": "keyword"},
                "message": {"type": "text"},
                # The "wrong" type we want to fix: numeric data stored as a
                # keyword, so range queries and aggregations do not work.
                "status_code": {"type": "keyword"},
            }
        },
        settings={"index": {"number_of_shards": 1, "number_of_replicas": 0}},
    )
    # Point both aliases at v1 to start with.
    es.indices.update_aliases(
        actions=[
            {"add": {"index": V1, "alias": WRITE_ALIAS}},
            {"add": {"index": V1, "alias": READ_ALIAS}},
        ]
    )


def seed_data() -> None:
    """Write a few documents THROUGH the write alias, as a client would."""
    docs = [
        {"@timestamp": "2024-01-01T00:00:00Z", "service": "api",
         "message": "ok", "status_code": "200"},
        {"@timestamp": "2024-01-01T00:01:00Z", "service": "api",
         "message": "missing", "status_code": "404"},
        {"@timestamp": "2024-01-01T00:02:00Z", "service": "api",
         "message": "boom", "status_code": "500"},
    ]
    for doc in docs:
        es.index(index=WRITE_ALIAS, document=doc)
    es.indices.refresh(index=WRITE_ALIAS)


def count(alias: str) -> int:
    """Return the document count visible through an alias or index name."""
    es.indices.refresh(index=alias)
    return es.count(index=alias)["count"]


def create_v2() -> None:
    """Create v2 with the FIXED mapping (status_code as an integer)."""
    es.indices.create(
        index=V2,
        mappings={
            "properties": {
                "@timestamp": {"type": "date"},
                "service": {"type": "keyword"},
                "message": {"type": "text"},
                # The corrected type. status_code is now a real integer, so
                # range queries and aggregations work.
                "status_code": {"type": "integer"},
            }
        },
        settings={"index": {"number_of_shards": 1, "number_of_replicas": 0}},
    )


def reindex_v1_to_v2() -> None:
    """Copy all documents from v1 into v2. v1 keeps serving reads."""
    result = es.reindex(
        body={"source": {"index": V1}, "dest": {"index": V2}},
        refresh=True,
        wait_for_completion=True,
    )
    print(f"reindex copied {result['total']} documents")


def swap_aliases() -> None:
    """Atomically repoint BOTH aliases from v1 to v2 in a single call.

    Because the remove and add actions execute as one transaction, there is
    no instant where app-read or app-write resolves to zero indices.
    """
    es.indices.update_aliases(
        actions=[
            {"remove": {"index": V1, "alias": READ_ALIAS}},
            {"remove": {"index": V1, "alias": WRITE_ALIAS}},
            {"add": {"index": V2, "alias": READ_ALIAS}},
            {"add": {"index": V2, "alias": WRITE_ALIAS}},
        ]
    )


def main() -> None:
    cleanup_previous()

    print("step 1: create v1 with the old mapping and seed data")
    create_v1()
    seed_data()
    before = count(READ_ALIAS)
    print(f"  documents visible through {READ_ALIAS}: {before}")
    resolved = list(es.indices.get_alias(name=READ_ALIAS).keys())
    print(f"  {READ_ALIAS} currently resolves to: {resolved}")

    print("step 2: create v2 with the corrected mapping")
    create_v2()

    print("step 3: reindex v1 -> v2 (reads still served by v1)")
    reindex_v1_to_v2()

    print("step 4: atomic alias swap (no zero-index window)")
    swap_aliases()

    after = count(READ_ALIAS)
    resolved = list(es.indices.get_alias(name=READ_ALIAS).keys())
    print(f"  {READ_ALIAS} now resolves to: {resolved}")
    print(f"  documents visible through {READ_ALIAS}: {after}")

    # Prove the swap was lossless and that the new mapping is in effect.
    assert before == after, f"count mismatch: {before} != {after}"
    mapping = es.indices.get_mapping(index=V2)
    new_type = mapping[V2]["mappings"]["properties"]["status_code"]["type"]
    print(f"  status_code type in active index is now: {new_type}")
    assert new_type == "integer"

    # A range query that was impossible on the keyword mapping now works.
    hits = es.search(
        index=READ_ALIAS,
        query={"range": {"status_code": {"gte": 400}}},
    )["hits"]["total"]["value"]
    print(f"  range query status_code>=400 returns {hits} hits (was impossible)")

    print("step 5: old index v1 can now be dropped safely")
    es.indices.delete(index=V1)
    print("SWAP COMPLETE: zero-downtime mapping change succeeded")


if __name__ == "__main__":
    main()
