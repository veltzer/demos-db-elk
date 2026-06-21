#!/usr/bin/env python
"""Add a new month behind the alias and move the write target onto it.

This is the recurring maintenance job for the hide-many-behind-one pattern:
once a month you create the next index, add it to the read alias so it
becomes searchable, and atomically move ``is_write_index`` from the old
month to the new one so new documents start landing in the new index. The
application keeps writing to and reading from the single name ``logs`` the
entire time and never notices the cutover.

We do all the alias changes in ONE ``_aliases`` call so there is never a
moment where two indices both claim to be the write index (which would make
writes ambiguous) or where the alias has no write index at all (which would
reject writes). Atomicity is the whole reason aliases are safe to operate
live.
"""

from elasticsearch import Elasticsearch

ES = "http://localhost:9200"
ALIAS = "logs"
OLD_MONTH = "logs-2026.06"
NEW_MONTH = "logs-2026.07"


def main() -> None:
    es = Elasticsearch(ES)

    # 1. Create the new month's index. It is just another ordinary index; it
    # is invisible to the application until we add it to the alias below.
    print(f"=== creating {NEW_MONTH} ===")
    if not es.indices.exists(index=NEW_MONTH):
        es.indices.create(
            index=NEW_MONTH,
            settings={"number_of_shards": 1, "number_of_replicas": 0},
            mappings={
                "properties": {
                    "@timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "service": {"type": "keyword"},
                    "message": {"type": "text"},
                }
            },
        )

    # 2. Atomically:
    #    - add the new month to the read alias (now searchable via "logs"),
    #    - make the new month the write index,
    #    - demote the old month so it stops receiving writes but stays
    #      readable (is_write_index:false, NOT removed from the alias).
    # All three happen together so the alias is always in a valid state.
    print("=== atomically repointing the write index onto the new month ===")
    es.indices.update_aliases(
        actions=[
            {"add": {"index": NEW_MONTH, "alias": ALIAS, "is_write_index": True}},
            {"add": {"index": OLD_MONTH, "alias": ALIAS, "is_write_index": False}},
        ]
    )

    # 3. Write a document through the alias and confirm it landed in the NEW
    # month, proving the write target moved without the writer changing.
    print("=== write through the alias, expect it in the new month ===")
    resp = es.index(
        index=ALIAS,
        document={
            "@timestamp": "2026-07-01T00:00:00Z",
            "level": "INFO",
            "service": "api",
            "message": "first july document via alias",
        },
        refresh=True,
    )
    print(f"document landed in: {resp['_index']}")
    assert resp["_index"] == NEW_MONTH, "write did not route to the new month!"

    # 4. Show the alias now spans four months with a single write index, and
    # that a read still fans out across every month.
    print("=== alias membership after the roll ===")
    for name, info in sorted(es.indices.get_alias(name=ALIAS).items()):
        meta = info["aliases"][ALIAS]
        is_write = meta.get("is_write_index", False)
        print(f"  {name:<16} is_write_index={is_write}")

    total = es.count(index=ALIAS)["count"]
    print(f"=== total documents visible through '{ALIAS}': {total} ===")


if __name__ == "__main__":
    main()
