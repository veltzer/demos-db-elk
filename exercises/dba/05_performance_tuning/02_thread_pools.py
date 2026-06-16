#!/usr/bin/env python
"""Inspect thread pools and flag any with rejections.

This wraps the data behind GET /_cat/thread_pool and highlights the
pools a DBA cares about most: `write` (indexing) and `search`.

Every thread pool has a fixed number of threads and a bounded queue.
When all threads are busy AND the queue is full, new tasks are
REJECTED. A rejection is not "slow", it is "dropped": the client sees
an es_rejected_execution_exception (HTTP 429). Rejections almost always
mean the cluster is being asked to do more concurrent work than it can
sustain.

REMEDIES (in rough order of preference):
  * Reduce client concurrency / batch size; add client-side retry with
    backoff (the bulk helpers already do this).
  * Spread load over more shards / nodes (scale out).
  * For search, reduce expensive queries, aggregations, and the number
    of shards hit per request.
  * Increasing queue_size only HIDES the problem and adds latency; it is
    a last resort, not a fix.
"""

from typing import Any

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

# Pools that are most interesting for a DBA tuning indexing/search load.
KEY_POOLS = {"write", "search", "get", "bulk", "search_throttled"}


def main() -> None:
    """Print thread-pool activity and flag rejections."""
    if not es.ping():
        print("Error: could not connect to Elasticsearch")
        return

    rows: Any = es.cat.thread_pool(
        h="node_name,name,active,queue,rejected,completed",
        format="json",
    )

    header = f"{'node':<16}{'pool':<18}{'act':>5}{'queue':>7}{'rej':>8}"
    print(header)
    print("-" * len(header))

    problems = []
    for r in rows:
        name = r["name"]
        active = int(r.get("active") or 0)
        queue = int(r.get("queue") or 0)
        rejected = int(r.get("rejected") or 0)

        # Keep the report readable: show key pools, plus anything that is
        # active, queued, or has ever rejected.
        if name not in KEY_POOLS and not (active or queue or rejected):
            continue

        flag = ""
        if rejected > 0:
            flag = "  <-- REJECTIONS"
            problems.append((r["node_name"], name, rejected))

        print(
            f"{r['node_name']:<16}{name:<18}"
            f"{active:>5}{queue:>7}{rejected:>8}{flag}"
        )

    print("-" * len(header))
    if problems:
        print("ALERT: rejections detected on these pools:")
        for node, pool, rej in problems:
            print(f"  {node} / {pool}: {rej} rejected task(s)")
        print(
            "Rejections (HTTP 429) mean work was DROPPED, not just slowed. "
            "Reduce concurrency/batch size and add retry-with-backoff; "
            "scale out before raising queue_size."
        )
    else:
        print("OK: no thread-pool rejections on any node.")


if __name__ == "__main__":
    main()
