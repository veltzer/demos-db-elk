#!/usr/bin/env python
"""Report JVM heap usage and garbage-collection activity per node.

This wraps GET /_nodes/stats/jvm and turns the raw numbers into a DBA
report: heap used percent, the size of the young/survivor/old memory
pools, and the cumulative GC collection counts and times for the young
and old collectors.

Heap pressure is the single most common cause of an unhealthy
Elasticsearch node. Two rules of thumb to remember:

  * Set the heap to <= 50% of physical RAM. The other half is left for
    the operating-system filesystem cache, which Lucene relies on for
    fast searches.
  * Keep the heap UNDER ~31GB. Above roughly 32GB the JVM can no longer
    use "compressed ordinary object pointers" (compressed oops), so a
    32GB heap can actually hold LESS usable data than a 30GB heap while
    making GC pauses longer.

You set the heap with jvm.options (see 02b_set_heap_notes.sh).
"""

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

MB = 1024 ** 2

# Above this heap-used percent the node is under memory pressure and is
# at risk of long GC pauses and circuit-breaker trips.
HEAP_WARN_PCT = 75
HEAP_HIGH_PCT = 85


def main() -> None:
    """Print a per-node JVM heap and GC summary."""
    if not es.ping():
        print("Error: could not connect to Elasticsearch")
        return

    stats = es.nodes.stats(metric="jvm")

    for node_id, node in stats["nodes"].items():
        name = node.get("name", node_id)
        jvm = node["jvm"]
        mem = jvm["mem"]

        used = mem["heap_used_in_bytes"]
        committed = mem["heap_committed_in_bytes"]
        max_heap = mem["heap_max_in_bytes"]
        used_pct = mem["heap_used_percent"]

        print("=" * 64)
        print(f"NODE: {name}")
        print("=" * 64)
        print(f"heap used:      {used / MB:8.1f} MB ({used_pct}%)")
        print(f"heap committed: {committed / MB:8.1f} MB")
        print(f"heap max:       {max_heap / MB:8.1f} MB")

        # Per-pool breakdown (young / survivor / old).
        print("-" * 64)
        print("memory pools (used / max):")
        for pool_name, pool in mem.get("pools", {}).items():
            p_used = pool.get("used_in_bytes", 0)
            p_max = pool.get("max_in_bytes", 0)
            print(
                f"  {pool_name:<10} "
                f"{p_used / MB:8.1f} MB / {p_max / MB:8.1f} MB"
            )

        # GC collectors: cumulative counts and total pause time.
        print("-" * 64)
        print("garbage collection (cumulative since node start):")
        collectors = jvm.get("gc", {}).get("collectors", {})
        for gc_name, gc in collectors.items():
            count = gc.get("collection_count", 0)
            millis = gc.get("collection_time_in_millis", 0)
            avg = (millis / count) if count else 0
            print(
                f"  {gc_name:<6} collections={count:<8} "
                f"total={millis} ms  avg={avg:.1f} ms"
            )

        # Heap-pressure flag.
        print("-" * 64)
        if used_pct >= HEAP_HIGH_PCT:
            print(
                f"ALERT: heap at {used_pct}% (>= {HEAP_HIGH_PCT}%). "
                "Node is under heavy memory pressure: expect long GC "
                "pauses and possible circuit-breaker trips."
            )
        elif used_pct >= HEAP_WARN_PCT:
            print(
                f"WARNING: heap at {used_pct}% (>= {HEAP_WARN_PCT}%). "
                "Watch GC times and consider more heap/nodes or less load."
            )
        else:
            print(f"OK: heap at {used_pct}%.")

    print("=" * 64)
    print(
        "Reminder: heap <= 50% of RAM and under ~31GB (compressed oops). "
        "Bigger is NOT always better."
    )


if __name__ == "__main__":
    main()
