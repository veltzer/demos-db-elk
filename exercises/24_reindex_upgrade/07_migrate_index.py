#!/usr/bin/env python

# End-to-end "migrate index" runbook in one script.
#
# This is the pattern you reach for when a production index has the wrong
# mapping and you need to fix it with zero downtime for readers. The trick
# is to point applications at an ALIAS rather than the real index, so you
# can swap the underlying index atomically once the new one is ready.
#
# Steps performed:
#   1. Create the OLD index (orders_v1) with a flawed mapping and load data.
#   2. Point the alias "orders" at orders_v1.
#   3. Create the NEW index (orders_v2) with the corrected mapping.
#   4. Reindex orders_v1 -> orders_v2 applying a transform script.
#   5. Verify document counts match and spot-check a sample document.
#   6. Atomically move the alias "orders" from orders_v1 to orders_v2.
#   7. Print PASS or FAIL.

import sys
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

OLD = "orders_v1"
NEW = "orders_v2"
ALIAS = "orders"


def cleanup():
    """Remove anything left over from a previous run so we are idempotent."""
    for idx in (OLD, NEW):
        if es.indices.exists(index=idx):
            es.indices.delete(index=idx)


def step_create_old():
    """Create the old index with a deliberately wrong mapping and load data.

    The flaws we will fix:
      - "status" is text (should be keyword for exact filtering/aggs).
      - "order_date" is text (should be a real date).
      - there is no "total" field yet (we will derive it).
    """
    es.indices.create(
        index=OLD,
        mappings={
            "properties": {
                "customer":   {"type": "text"},
                "status":     {"type": "text"},
                "order_date": {"type": "text"},
                "quantity":   {"type": "integer"},
                "unit_price": {"type": "float"},
            }
        },
        settings={"index": {"number_of_shards": 1, "number_of_replicas": 0}},
    )

    docs = [
        {"customer": "alice", "status": "shipped",
         "order_date": "2024-01-10", "quantity": 2, "unit_price": 9.5},
        {"customer": "bob", "status": "pending",
         "order_date": "2024-01-12", "quantity": 1, "unit_price": 40.0},
        {"customer": "carol", "status": "shipped",
         "order_date": "2024-02-01", "quantity": 5, "unit_price": 3.0},
        {"customer": "dave", "status": "cancelled",
         "order_date": "2024-02-15", "quantity": 3, "unit_price": 12.0},
    ]
    for doc in docs:
        es.index(index=OLD, document=doc)
    es.indices.refresh(index=OLD)

    # Reads go through the alias from day one.
    es.indices.put_alias(index=OLD, name=ALIAS)
    print(f"[1] created {OLD} with {len(docs)} docs, alias '{ALIAS}' -> {OLD}")


def step_create_new():
    """Create the new index with the corrected mapping (including 'total')."""
    es.indices.create(
        index=NEW,
        mappings={
            "properties": {
                "customer":   {"type": "text"},
                "status":     {"type": "keyword"},
                "order_date": {"type": "date"},
                "quantity":   {"type": "integer"},
                "unit_price": {"type": "float"},
                "total":      {"type": "float"},
            }
        },
        settings={"index": {"number_of_shards": 1, "number_of_replicas": 0}},
    )
    print(f"[2] created {NEW} with corrected mapping (status=keyword, "
          f"order_date=date, +total)")


def step_reindex():
    """Reindex old -> new, deriving 'total' = quantity * unit_price."""
    resp = es.reindex(
        body={
            "source": {"index": OLD},
            "dest": {"index": NEW},
            "script": {
                "lang": "painless",
                "source": (
                    "ctx._source.total = "
                    "ctx._source.quantity * ctx._source.unit_price;"
                ),
            },
        },
        refresh=True,
        wait_for_completion=True,
    )
    print(f"[3] reindexed: created={resp['created']} "
          f"failures={len(resp['failures'])} took={resp['took']}ms")
    return resp


def step_verify():
    """Verify counts match and spot-check one document in the new index."""
    old_count = es.count(index=OLD)["count"]
    new_count = es.count(index=NEW)["count"]
    print(f"[4] counts: {OLD}={old_count}  {NEW}={new_count}")
    if old_count != new_count:
        return False, "document counts differ"

    # Spot-check: pull one shipped order and confirm the derived total and
    # that status is now a real keyword we can filter on exactly.
    hit = es.search(
        index=NEW,
        query={"term": {"status": "shipped"}},
        size=1,
    )
    if hit["hits"]["total"]["value"] == 0:
        return False, "keyword term query on status returned nothing"

    src = hit["hits"]["hits"][0]["_source"]
    expected_total = src["quantity"] * src["unit_price"]
    print(f"[5] sample doc: customer={src['customer']} "
          f"status={src['status']} total={src['total']} "
          f"(expected {expected_total})")
    if abs(src["total"] - expected_total) > 1e-6:
        return False, "derived 'total' is wrong"

    return True, "counts match and sample doc is correct"


def step_swap_alias():
    """Atomically move the alias from the old index to the new one.

    Doing both actions in one _aliases call means readers never see a moment
    where 'orders' points at nothing. This is the zero-downtime cutover.
    """
    es.indices.update_aliases(
        body={
            "actions": [
                {"remove": {"index": OLD, "alias": ALIAS}},
                {"add": {"index": NEW, "alias": ALIAS}},
            ]
        }
    )
    target = list(es.indices.get_alias(name=ALIAS).keys())
    print(f"[6] alias '{ALIAS}' now -> {target}")
    return target == [NEW]


def main():
    cleanup()
    step_create_old()
    step_create_new()
    step_reindex()
    ok, msg = step_verify()
    if not ok:
        print(f"FAIL: verification failed - {msg}")
        sys.exit(1)

    if not step_swap_alias():
        print("FAIL: alias did not point at the new index")
        sys.exit(1)

    print(f"RESULT: {msg}")
    print("PASS")


if __name__ == "__main__":
    main()
