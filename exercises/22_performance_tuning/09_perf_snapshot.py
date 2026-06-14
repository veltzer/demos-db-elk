#!/usr/bin/env python
"""Consolidated performance snapshot with simple WARN/OK flags.

This is the "one screen a DBA glances at" report. It pulls together the
four operational signals from the earlier scripts into a single pass:

  * JVM heap used percent (per node)
  * thread-pool rejections (write / search)
  * circuit-breaker trips
  * query / request cache hit ratios

Each line is tagged OK / WARN / ALERT so problems jump out. The exit
status is non-zero if anything is in ALERT, so this script can also be
dropped into a cron job or a CI health gate.
"""

import sys
from typing import Any

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

HEAP_WARN = 75
HEAP_ALERT = 85

OK, WARN, ALERT = "OK", "WARN", "ALERT"


def tag(level: str, msg: str) -> str:
    """Format one report line with its severity tag."""
    return f"[{level:<5}] {msg}"


def hit_ratio(cache: dict) -> float:
    """Return a cache hit ratio in percent, or -1.0 when cold."""
    total = cache["hit_count"] + cache["miss_count"]
    if total == 0:
        return -1.0
    return 100.0 * cache["hit_count"] / total


def main() -> int:
    """Print the consolidated snapshot and return a process exit code."""
    if not es.ping():
        print("Error: could not connect to Elasticsearch")
        return 2

    worst = OK

    def note(level: str, msg: str) -> None:
        nonlocal worst
        if level == ALERT or (level == WARN and worst != ALERT):
            worst = level
        print(tag(level, msg))

    print("=" * 64)
    print("ELASTICSEARCH PERFORMANCE SNAPSHOT")
    print("=" * 64)

    # --- heap + breakers (one stats call) -----------------------------
    jvm_stats = es.nodes.stats(metric=["jvm", "breaker"])
    print("-- heap --")
    for node in jvm_stats["nodes"].values():
        name = node.get("name", "?")
        pct = node["jvm"]["mem"]["heap_used_percent"]
        if pct >= HEAP_ALERT:
            note(ALERT, f"{name}: heap {pct}% (>= {HEAP_ALERT}%)")
        elif pct >= HEAP_WARN:
            note(WARN, f"{name}: heap {pct}% (>= {HEAP_WARN}%)")
        else:
            note(OK, f"{name}: heap {pct}%")

    print("-- circuit breakers --")
    for node in jvm_stats["nodes"].values():
        name = node.get("name", "?")
        tripped = {
            b: d.get("tripped", 0)
            for b, d in node["breakers"].items()
            if d.get("tripped", 0) > 0
        }
        if tripped:
            note(ALERT, f"{name}: breaker trips {tripped}")
        else:
            note(OK, f"{name}: no breaker trips")

    # --- thread-pool rejections ---------------------------------------
    print("-- thread pools --")
    rows: Any = es.cat.thread_pool(
        h="node_name,name,rejected", format="json"
    )
    any_rej = False
    for r in rows:
        rej = int(r.get("rejected") or 0)
        if rej > 0 and r["name"] in ("write", "search", "bulk", "get"):
            any_rej = True
            note(ALERT, f"{r['node_name']}/{r['name']}: {rej} rejections")
    if not any_rej:
        note(OK, "no write/search rejections")

    # --- cache hit ratios ---------------------------------------------
    print("-- caches --")
    cache_stats = es.nodes.stats(
        metric="indices", index_metric="query_cache,request_cache"
    )
    for node in cache_stats["nodes"].values():
        name = node.get("name", "?")
        for label, key in (("query", "query_cache"),
                            ("request", "request_cache")):
            r = hit_ratio(node["indices"][key])
            if r < 0:
                note(OK, f"{name}: {label} cache cold (no traffic yet)")
            elif r < 30:
                note(WARN, f"{name}: {label} cache hit ratio {r:.0f}%")
            else:
                note(OK, f"{name}: {label} cache hit ratio {r:.0f}%")

    print("=" * 64)
    print(f"OVERALL: {worst}")
    return 1 if worst == ALERT else 0


if __name__ == "__main__":
    sys.exit(main())
