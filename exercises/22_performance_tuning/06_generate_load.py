#!/usr/bin/env python
"""Create a demo index and load enough data to make the stats interesting.

This gives the rest of the exercise something to measure. It creates the
`perf_demo` index with a sensible mapping (a `keyword` field for safe
aggregation and a `text` field for searching) and bulk-loads fake
documents. It then runs a few repeated filter + aggregation queries so
the query/request caches and thread pools show non-zero activity when
you inspect them.

Run this once before the inspection scripts so they have real numbers to
report.
"""

import random
from typing import Any

from elasticsearch import Elasticsearch
from elasticsearch import helpers

fake: Any
try:
    from faker import Faker
    fake = Faker()
except ImportError:  # faker is optional; fall back to canned values.
    fake = None

es = Elasticsearch("http://localhost:9200")

INDEX = "perf_demo"
DOC_COUNT = 20000

DEPARTMENTS = ["sales", "engineering", "support", "marketing", "finance"]
CITIES = ["london", "paris", "berlin", "madrid", "rome", "lisbon"]


def sentence() -> str:
    """Return a short text blob, using faker when available."""
    if fake:
        return fake.sentence(nb_words=12)
    return " ".join(random.choice(CITIES) for _ in range(12))


def create_index() -> None:
    """(Re)create the demo index with an explicit mapping."""
    es.options(ignore_status=404).indices.delete(index=INDEX)
    es.indices.create(
        index=INDEX,
        mappings={
            "properties": {
                # keyword -> aggregate/sort safely via doc_values.
                "department": {"type": "keyword"},
                "city": {"type": "keyword"},
                # text -> full-text search (do NOT aggregate on this).
                "bio": {"type": "text"},
                "salary": {"type": "integer"},
                "age": {"type": "integer"},
            }
        },
        settings={
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
            }
        },
    )


def gen_docs():
    """Yield bulk action dicts for the demo documents."""
    for i in range(DOC_COUNT):
        yield {
            "_index": INDEX,
            "_id": i,
            "department": random.choice(DEPARTMENTS),
            "city": random.choice(CITIES),
            "bio": sentence(),
            "salary": random.randint(30000, 200000),
            "age": random.randint(21, 65),
        }


def warm_caches() -> None:
    """Run repeated filter + size=0 agg queries to warm the caches."""
    es.indices.refresh(index=INDEX)
    for _ in range(20):
        es.search(
            index=INDEX,
            size=0,
            query={"bool": {"filter": [{"term": {"department": "sales"}}]}},
            aggs={"by_city": {"terms": {"field": "city"}}},
            request_cache=True,
        )


def main() -> None:
    """Create the index, bulk load, and warm the caches."""
    if not es.ping():
        print("Error: could not connect to Elasticsearch")
        return

    print(f"creating index '{INDEX}'...")
    create_index()

    print(f"bulk loading {DOC_COUNT} documents...")
    success, _ = helpers.bulk(es, gen_docs(), chunk_size=2000)
    print(f"indexed {success} documents")

    print("warming query/request caches with repeated aggregations...")
    warm_caches()

    print("done. Now run the inspection scripts (01..04, 07).")


if __name__ == "__main__":
    main()
