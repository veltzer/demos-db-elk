#!/usr/bin/env python
"""Simple disk capacity planner / storage forecaster for a DBA.

Given the current store size and document count of an index, plus an estimate
of how many new documents arrive per day, this script projects:

  * average bytes per document (store size / doc count)
  * how many MB/GB the index grows per day
  * how many days until the data node's free disk is exhausted

It reads live numbers straight from Elasticsearch:
  * per-index store size and doc count from GET /_cat/indices
  * free/total disk per node from GET /_cat/allocation

You supply the expected ingest rate (docs/day) on the command line; in a real
deployment you would derive this from your actual traffic (e.g. the doc-count
delta between two days of time-based indices).

Usage:
    ./08_capacity_forecast.py [index_name] [docs_per_day]

Example:
    ./08_capacity_forecast.py capacity_demo 2000000
"""

import sys

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")


def human(num_bytes):
    """Format a byte count as a human-readable string."""
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024.0:
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{value:.2f} PB"


def index_stats(index):
    """Return (store_bytes, doc_count) for an index via _cat/indices."""
    rows = es.cat.indices(
        index=index,
        format="json",
        bytes="b",
        h="index,docs.count,store.size",
    )
    if not rows:
        print(f"Error: index '{index}' not found")
        sys.exit(1)
    row = rows[0]
    return int(row["store.size"]), int(row["docs.count"])


def min_free_disk():
    """Return the smallest free-disk (bytes) across all data nodes.

    A cluster fills up at the rate of its FULLEST node, so the most
    conservative forecast uses the node with the least free disk.
    """
    rows = es.cat.allocation(
        format="json", bytes="b", h="node,disk.avail,disk.total,disk.percent"
    )
    frees = []
    for row in rows:
        avail = row.get("disk.avail")
        # Unassigned-shard pseudo-rows have no disk info; skip them.
        if avail not in (None, "", "null"):
            frees.append((row["node"], int(avail), row.get("disk.percent")))
    if not frees:
        print("Error: no data-node disk info from _cat/allocation")
        sys.exit(1)
    return min(frees, key=lambda r: r[1])


def main():
    index = sys.argv[1] if len(sys.argv) > 1 else "capacity_demo"
    docs_per_day = int(sys.argv[2]) if len(sys.argv) > 2 else 2_000_000

    if not es.ping():
        print("Error: could not connect to Elasticsearch")
        sys.exit(1)

    store_bytes, doc_count = index_stats(index)
    if doc_count == 0:
        print(f"Error: index '{index}' has no documents to base a forecast on")
        sys.exit(1)

    bytes_per_doc = store_bytes / doc_count
    growth_per_day = bytes_per_doc * docs_per_day

    node, free_bytes, pct = min_free_disk()
    # Forecast against the high watermark (90%), not 100%: once you cross it ES
    # stops placing shards here, which is the practical "full" for a DBA.
    usable_bytes = free_bytes  # free disk on the tightest node right now
    days_until_full = (
        usable_bytes / growth_per_day if growth_per_day > 0 else float("inf")
    )

    print("=" * 64)
    print(f"CAPACITY FORECAST for index '{index}'")
    print("=" * 64)
    print(f"current store size:     {human(store_bytes)}")
    print(f"current doc count:      {doc_count:,}")
    print(f"avg bytes / document:   {human(bytes_per_doc)}")
    print("-" * 64)
    print(f"assumed ingest rate:    {docs_per_day:,} docs/day")
    print(f"projected growth/day:   {human(growth_per_day)}")
    print(f"projected growth/week:  {human(growth_per_day * 7)}")
    print(f"projected growth/month: {human(growth_per_day * 30)}")
    print("-" * 64)
    print(f"tightest data node:     {node} ({pct}% used)")
    print(f"free disk on that node: {human(free_bytes)}")
    print("-" * 64)
    if days_until_full == float("inf"):
        print("days until full:        never (no growth)")
    else:
        print(f"days until full:        {days_until_full:,.1f} days")
        print(
            "ACTION BY (approx):     in "
            f"{int(days_until_full)} days you cross the disk limit."
        )
        if days_until_full < 30:
            print(
                "WARNING: under 30 days of headroom. Plan to add disk/nodes, "
                "delete old data, or move indices to a cheaper tier NOW."
            )
    print("=" * 64)


if __name__ == "__main__":
    main()
