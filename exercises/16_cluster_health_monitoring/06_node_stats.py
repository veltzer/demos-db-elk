#!/usr/bin/env python
"""Pull per-node JVM, GC and thread-pool stats into a table.

Wraps GET /_nodes/stats and extracts the metrics a DBA watches most:
  - JVM heap used %  (sustained > 75% is a warning sign)
  - GC collection counts and total time (frequent/long GC = memory pressure)
  - thread-pool rejections (rejections mean the cluster is overloaded and
    is dropping work for search/write/etc.)
"""

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

# Thread pools a DBA most cares about for rejection counts.
WATCH_POOLS = ["search", "write", "get", "bulk", "snapshot"]


def main() -> None:
    """Print a per-node stats table."""
    stats = es.nodes.stats(metric=["jvm", "thread_pool", "os", "process"])

    print(
        f"{'node':<20} {'heap%':>6} {'heap_used':>10} "
        f"{'gc_young':>9} {'gc_old':>7} {'gc_ms':>8} {'cpu%':>5}"
    )
    print("-" * 70)

    rejection_lines = []
    for node_id, node in stats["nodes"].items():
        name = node.get("name", node_id)[:19]
        jvm = node["jvm"]
        mem = jvm["mem"]
        heap_pct = mem["heap_used_percent"]
        heap_used_mb = mem["heap_used_in_bytes"] / (1024 * 1024)

        collectors = jvm["gc"]["collectors"]
        young = collectors.get("young", {})
        old = collectors.get("old", {})
        gc_young = young.get("collection_count", 0)
        gc_old = old.get("collection_count", 0)
        gc_ms = young.get("collection_time_in_millis", 0) + old.get(
            "collection_time_in_millis", 0
        )

        cpu = node.get("process", {}).get("cpu", {}).get("percent", 0)

        flag = " <-- HIGH HEAP" if heap_pct >= 75 else ""
        print(
            f"{name:<20} {heap_pct:>6} {heap_used_mb:>9.0f}M "
            f"{gc_young:>9} {gc_old:>7} {gc_ms:>8} {cpu:>5}{flag}"
        )

        # Collect thread-pool rejections to report after the table.
        pools = node.get("thread_pool", {})
        for pool_name in WATCH_POOLS:
            pool = pools.get(pool_name)
            if pool and pool.get("rejected", 0) > 0:
                rejection_lines.append(
                    f"  {name}: {pool_name} rejected="
                    f"{pool['rejected']} (queue={pool.get('queue', 0)})"
                )

    print("-" * 70)
    print("thread-pool rejections (DBA should investigate any > 0):")
    if rejection_lines:
        for line in rejection_lines:
            print(line)
    else:
        print("  none - no thread-pool rejections on any node.")


if __name__ == "__main__":
    main()
