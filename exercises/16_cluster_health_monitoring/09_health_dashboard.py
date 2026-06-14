#!/usr/bin/env python
"""Consolidated one-screen cluster health dashboard.

Polls several monitoring APIs and prints a single compact report a DBA
can glance at: cluster status, per-node heap/cpu/disk, unassigned shard
count, thread-pool rejections, and pending tasks.

Run once for a snapshot, or pass an interval in seconds to refresh:
    ./09_health_dashboard.py          # single snapshot
    ./09_health_dashboard.py 5        # refresh every 5 seconds
"""

import sys
import time
from datetime import datetime

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

HEAP_WARN = 75
DISK_WARN = 85


def collect():
    """Gather all the data the dashboard needs in one pass."""
    health = es.cluster.health()
    node_stats = es.nodes.stats(
        metric=["jvm", "os", "fs", "thread_pool", "process"]
    )
    pending = es.cluster.pending_tasks().get("tasks", [])
    return health, node_stats, pending


def render(health, node_stats, pending) -> None:
    """Print the dashboard to stdout."""
    status = health["status"].upper()
    banner = {
        "GREEN": "GREEN  (healthy)",
        "YELLOW": "YELLOW (replicas unassigned)",
        "RED": "RED    (PRIMARY SHARDS MISSING!)",
    }.get(status, status)

    print("=" * 64)
    print(
        f"  CLUSTER HEALTH DASHBOARD   {datetime.now():%Y-%m-%d %H:%M:%S}"
    )
    print("=" * 64)
    print(f"cluster : {health['cluster_name']}")
    print(f"status  : {banner}")
    print(
        f"nodes   : {health['number_of_nodes']} "
        f"(data: {health['number_of_data_nodes']})    "
        f"shards active: {health['active_shards']}  "
        f"unassigned: {health['unassigned_shards']}  "
        f"relocating: {health['relocating_shards']}  "
        f"initializing: {health['initializing_shards']}"
    )
    print(
        f"pending cluster-state tasks: {len(pending)}    "
        f"active shards: "
        f"{health['active_shards_percent_as_number']:.1f}%"
    )

    print("-" * 64)
    print(
        f"{'node':<18} {'heap%':>5} {'cpu%':>5} {'disk%':>6} "
        f"{'load1m':>7}  rejections"
    )
    print("-" * 64)

    for node_id, node in node_stats["nodes"].items():
        name = node.get("name", node_id)[:17]
        heap = node["jvm"]["mem"]["heap_used_percent"]
        cpu = node.get("process", {}).get("cpu", {}).get("percent", 0)

        fs_total = node.get("fs", {}).get("total", {})
        total_b = fs_total.get("total_in_bytes", 0)
        avail_b = fs_total.get("available_in_bytes", 0)
        disk_pct = 0
        if total_b:
            disk_pct = (total_b - avail_b) / total_b * 100

        load1m = node.get("os", {}).get("cpu", {}).get(
            "load_average", {}
        ).get("1m", 0)

        rejected = 0
        for pool in node.get("thread_pool", {}).values():
            rejected += pool.get("rejected", 0)

        flags = ""
        if heap >= HEAP_WARN:
            flags += " HEAP"
        if disk_pct >= DISK_WARN:
            flags += " DISK"
        if rejected:
            flags += " REJECT"

        print(
            f"{name:<18} {heap:>5} {cpu:>5} {disk_pct:>5.0f}% "
            f"{load1m:>7.2f}  {rejected:>9}{flags}"
        )

    print("-" * 64)
    alerts = []
    if status == "RED":
        alerts.append("RED cluster: primary shards missing.")
    if health["unassigned_shards"] > 0:
        alerts.append(
            f"{health['unassigned_shards']} unassigned shard(s)."
        )
    if len(pending) > 0:
        alerts.append(f"{len(pending)} pending cluster-state task(s).")
    if alerts:
        print("ALERTS:")
        for a in alerts:
            print(f"  ! {a}")
    else:
        print("no alerts - cluster looks healthy.")
    print("=" * 64)


def main() -> None:
    """Render once, or loop on an interval if one was supplied."""
    interval = None
    if len(sys.argv) > 1:
        interval = float(sys.argv[1])

    while True:
        data = collect()
        if interval:
            # Clear screen for a live dashboard feel.
            print("\033[2J\033[H", end="")
        render(*data)
        if not interval:
            break
        time.sleep(interval)


if __name__ == "__main__":
    main()
