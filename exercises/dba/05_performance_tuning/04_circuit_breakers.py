#!/usr/bin/env python
"""Report circuit-breaker limits and trip counts per node.

This wraps GET /_nodes/stats/breaker. Circuit breakers are
Elasticsearch's last line of defence against an OutOfMemoryError: before
a request can allocate enough memory to crash the JVM, the relevant
breaker "trips" and the request fails with a CircuitBreakingException
(HTTP 429). A tripped breaker protects the NODE at the cost of one
request.

The breakers you will see:

  * parent     - the overall cap across all child breakers. By default
                 ~95% of the heap (the "real memory" circuit breaker
                 also watches actual heap usage). A tripping parent
                 breaker is the clearest sign the node is short on heap.
  * fielddata  - caps memory used by fielddata (text sort/agg). Trips
                 here usually mean someone is aggregating on a text
                 field; switch to a keyword sub-field.
  * request    - caps memory used to build a single request's data
                 structures (e.g. large aggregations).
  * in_flight_requests - caps the memory of in-flight transport/HTTP
                 request bytes.

Any non-zero `tripped` count deserves investigation: a request was
rejected to keep the node alive.
"""

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

MB = 1024 ** 2

# Breakers in the order a DBA usually scans them.
ORDER = ["parent", "fielddata", "request", "in_flight_requests", "accounting"]


def main() -> None:
    """Print breaker limits, current usage and trip counts."""
    if not es.ping():
        print("Error: could not connect to Elasticsearch")
        return

    stats = es.nodes.stats(metric="breaker")

    any_tripped = False
    for node_id, node in stats["nodes"].items():
        name = node.get("name", node_id)
        breakers = node["breakers"]

        print("=" * 70)
        print(f"NODE: {name}")
        print("=" * 70)
        print(
            f"{'breaker':<20}{'limit':>12}{'estimated':>12}"
            f"{'overhead':>10}{'tripped':>9}"
        )
        print("-" * 70)

        # Show known breakers first, then any extras.
        names = [b for b in ORDER if b in breakers]
        names += [b for b in breakers if b not in ORDER]

        for b in names:
            data = breakers[b]
            limit = data["limit_size_in_bytes"]
            est = data["estimated_size_in_bytes"]
            overhead = data.get("overhead", 1.0)
            tripped = data.get("tripped", 0)
            if tripped:
                any_tripped = True
            limit_s = "unbounded" if limit < 0 else f"{limit / MB:.0f}MB"
            print(
                f"{b:<20}{limit_s:>12}{est / MB:>11.1f}M"
                f"{overhead:>10.2f}{tripped:>9}"
            )

    print("=" * 70)
    if any_tripped:
        print(
            "ALERT: one or more breakers have tripped. Requests were "
            "rejected to protect the node from OOM. Investigate heap "
            "pressure (01_jvm_heap_gc.py) and check for fielddata on "
            "text fields and overly large aggregations."
        )
    else:
        print("OK: no circuit breakers have tripped.")


if __name__ == "__main__":
    main()
