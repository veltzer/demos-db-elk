#!/usr/bin/env python
"""Report Elasticsearch cache usage and hit ratios per node.

This wraps GET /_nodes/stats/indices/query_cache,request_cache,fielddata
and explains the three caches a DBA tunes:

  * query cache (a.k.a. node query cache): caches the results of filter
    clauses (the non-scoring parts of a query) as bitsets. Shared across
    the node. Helps repeated filters a lot.

  * request cache (shard request cache): caches the WHOLE response of a
    request when size=0 (typically aggregation/count results). Only used
    for size=0 requests and only on shards that are not refreshing.
    Toggle per index with index.requests.cache.enable (default true).

  * fielddata: in-memory data structure used for sorting/aggregating on
    TEXT fields. It is EXPENSIVE and a classic out-of-memory cause.
    DO NOT enable fielddata on text fields. Instead aggregate/sort on a
    `keyword` sub-field, which uses on-disk doc_values for free.

A high `evictions` count relative to cache size means the cache is too
small for the workload (entries are being pushed out before reuse).
"""

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

MB = 1024 ** 2


def ratio(hits: int, misses: int) -> str:
    """Format a cache hit ratio, guarding against divide-by-zero."""
    total = hits + misses
    if total == 0:
        return "n/a (cold)"
    return f"{100.0 * hits / total:.1f}%"


def main() -> None:
    """Print per-node cache statistics with hit ratios."""
    if not es.ping():
        print("Error: could not connect to Elasticsearch")
        return

    stats = es.nodes.stats(
        metric="indices",
        index_metric="query_cache,request_cache,fielddata",
    )

    for node_id, node in stats["nodes"].items():
        name = node.get("name", node_id)
        idx = node["indices"]
        qc = idx["query_cache"]
        rc = idx["request_cache"]
        fd = idx["fielddata"]

        print("=" * 64)
        print(f"NODE: {name}")
        print("=" * 64)

        print("query cache (filter bitsets):")
        print(
            f"  size={qc['memory_size_in_bytes'] / MB:.2f} MB  "
            f"hits={qc['hit_count']}  misses={qc['miss_count']}  "
            f"evictions={qc['evictions']}  "
            f"hit_ratio={ratio(qc['hit_count'], qc['miss_count'])}"
        )

        print("request cache (size=0 aggregation/count responses):")
        print(
            f"  size={rc['memory_size_in_bytes'] / MB:.2f} MB  "
            f"hits={rc['hit_count']}  misses={rc['miss_count']}  "
            f"evictions={rc['evictions']}  "
            f"hit_ratio={ratio(rc['hit_count'], rc['miss_count'])}"
        )

        print("fielddata (text sort/agg -- should usually stay tiny):")
        fd_mb = fd["memory_size_in_bytes"] / MB
        print(
            f"  size={fd_mb:.2f} MB  evictions={fd['evictions']}"
        )
        if fd_mb > 0:
            print(
                "  NOTE: fielddata is in use. Confirm you are not "
                "aggregating/sorting on TEXT fields; prefer keyword "
                "sub-fields (doc_values) instead."
            )

    print("=" * 64)
    print(
        "Tip: clear caches to re-measure cold-vs-warm behaviour with "
        "03b_clear_cache.sh. Low hit ratios after warm-up suggest the "
        "cache is too small or queries are not repetitive."
    )


if __name__ == "__main__":
    main()
