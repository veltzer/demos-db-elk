#!/usr/bin/env python
"""Reusable Elasticsearch metrics collector for DBA monitoring.

This module polls several cluster APIs and flattens the interesting bits
into a single dict of key/value metrics. Other scripts in this exercise
import collect_metrics() and build on top of it (threshold checks,
self-monitoring index, sampling loops).

APIs used:
  - GET /_cluster/health        cluster status, shards, pending tasks
  - GET /_nodes/stats           heap, gc, thread-pool rejections
  - GET /_cat/indices           index count and total store size
  - GET /_cluster/allocation/... disk usage / watermark headroom

Run directly to print the collected metrics as JSON:

    ./01_metrics_collector.py

Security is disabled (plain HTTP, no auth), as in the rest of the course.
"""

import json
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")


def _sum_thread_pool_rejections(node_stats):
    """Sum thread-pool rejections across all pools on one node.

    Rejections mean the node refused work because a queue was full. Any
    non-zero value (especially on the write/search pools) is a red flag.
    """
    total = 0
    pools = node_stats.get("thread_pool", {})
    for pool in pools.values():
        total += pool.get("rejected", 0)
    return total


def _disk_usage_percent(node_stats):
    """Return the highest disk-usage percentage across the node's data paths.

    We report the worst (fullest) filesystem because that is the one that
    will trip Elasticsearch's disk watermarks first.
    """
    worst = 0.0
    fs = node_stats.get("fs", {})
    for data_path in fs.get("data", []):
        total = data_path.get("total_in_bytes", 0)
        available = data_path.get("available_in_bytes", 0)
        if total > 0:
            used_pct = (total - available) / total * 100.0
            worst = max(worst, used_pct)
    # Fall back to the rolled-up fs.total if per-path data is missing.
    if worst == 0.0:
        total = fs.get("total", {}).get("total_in_bytes", 0)
        available = fs.get("total", {}).get("available_in_bytes", 0)
        if total > 0:
            worst = (total - available) / total * 100.0
    return worst


def collect_metrics():
    """Poll Elasticsearch and return a flat dict of key DBA metrics.

    The returned dict is intentionally flat (no nesting) so it is trivial
    to print, threshold-check, or index back into Elasticsearch as a
    monitoring document.
    """
    metrics = {}

    # ---- Cluster health --------------------------------------------------
    health = es.cluster.health()
    metrics["cluster_name"] = health["cluster_name"]
    metrics["status"] = health["status"]
    metrics["number_of_nodes"] = health["number_of_nodes"]
    metrics["number_of_data_nodes"] = health["number_of_data_nodes"]
    metrics["active_primary_shards"] = health["active_primary_shards"]
    metrics["active_shards"] = health["active_shards"]
    metrics["relocating_shards"] = health["relocating_shards"]
    metrics["initializing_shards"] = health["initializing_shards"]
    metrics["unassigned_shards"] = health["unassigned_shards"]
    metrics["pending_tasks"] = health["number_of_pending_tasks"]
    metrics["active_shards_percent"] = health[
        "active_shards_percent_as_number"
    ]

    # ---- Node stats: heap, gc, thread-pool rejections, disk --------------
    node_stats = es.nodes.stats(
        metric=["jvm", "thread_pool", "fs"]
    )
    heap_used_max = 0.0
    gc_collection_ms = 0
    rejections = 0
    disk_used_max = 0.0

    for node in node_stats["nodes"].values():
        jvm = node.get("jvm", {})
        mem = jvm.get("mem", {})
        heap_pct = mem.get("heap_used_percent", 0)
        heap_used_max = max(heap_used_max, float(heap_pct))

        collectors = jvm.get("gc", {}).get("collectors", {})
        for collector in collectors.values():
            gc_collection_ms += collector.get(
                "collection_time_in_millis", 0
            )

        rejections += _sum_thread_pool_rejections(node)
        disk_used_max = max(disk_used_max, _disk_usage_percent(node))

    metrics["heap_used_percent_max"] = round(heap_used_max, 1)
    metrics["gc_collection_time_ms_total"] = gc_collection_ms
    metrics["thread_pool_rejections_total"] = rejections
    metrics["disk_used_percent_max"] = round(disk_used_max, 1)

    # ---- Index count and total store size --------------------------------
    # _cat/indices with bytes=b gives machine-readable byte counts.
    indices = es.cat.indices(format="json", bytes="b", h="index,store.size")
    total_store_bytes = 0
    index_count = 0
    for row in indices:
        index_count += 1
        size = row.get("store.size") or "0"
        try:
            total_store_bytes += int(size)
        except (TypeError, ValueError):
            pass
    metrics["index_count"] = index_count
    metrics["total_store_bytes"] = total_store_bytes
    metrics["total_store_gb"] = round(total_store_bytes / 1024 ** 3, 3)

    return metrics


def main():
    """Collect once and print the metrics as pretty JSON."""
    metrics = collect_metrics()
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
