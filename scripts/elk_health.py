#!/usr/bin/env python
"""General ELK / Elasticsearch health check.

A richer counterpart to elk_health.sh. It uses the official Elasticsearch
Python client to gather cluster health, node stats, unassigned shards and
per-index status, then prints a single human-readable report with simple
DBA-style alerting at the end.

Override the target with the ES_URL environment variable, e.g.
    ES_URL=http://my-host:9200 ./elk_health.py
"""

import os

from elasticsearch import Elasticsearch

ES_URL = os.environ.get("ES_URL", "http://localhost:9200")

STATUS_MEANING = {
    "green": "All primary and replica shards are allocated.",
    "yellow": (
        "All primaries are allocated, but some replicas are not. Data is "
        "available with reduced redundancy (common on single-node clusters)."
    ),
    "red": (
        "At least one PRIMARY shard is unallocated. Some data is missing -- "
        "investigate immediately."
    ),
}


def main() -> None:
    """Gather and print a general cluster health report."""
    es = Elasticsearch(ES_URL)

    print("=" * 60)
    print(f"TARGET: {ES_URL}")

    health = es.cluster.health()
    status = health["status"]
    print(f"CLUSTER: {health['cluster_name']}")
    print(f"STATUS:  {status.upper()}")
    print("=" * 60)
    print(STATUS_MEANING.get(status, "Unknown status."))

    print("-" * 60)
    print(f"nodes (total):          {health['number_of_nodes']}")
    print(f"data nodes:             {health['number_of_data_nodes']}")
    print(f"active primary shards:  {health['active_primary_shards']}")
    print(f"active shards (total):  {health['active_shards']}")
    print(f"relocating shards:      {health['relocating_shards']}")
    print(f"initializing shards:    {health['initializing_shards']}")
    print(f"unassigned shards:      {health['unassigned_shards']}")
    print(
        "active shards percent:  "
        f"{health['active_shards_percent_as_number']:.1f}%"
    )
    print(f"pending tasks:          {health['number_of_pending_tasks']}")

    # Per-node heap and cpu, pulled from the nodes stats API.
    print("-" * 60)
    print("nodes:")
    stats = es.nodes.stats(metric="jvm,os")
    for node in stats["nodes"].values():
        name = node["name"]
        heap = node["jvm"]["mem"]["heap_used_percent"]
        cpu = node["os"]["cpu"]["percent"]
        print(f"  {name:<24} heap={heap:>3}%  cpu={cpu:>3}%")

    # List unassigned shards with their reason, if any.
    print("-" * 60)
    shards = es.cat.shards(
        h="index,shard,prirep,state,unassigned.reason", format="json"
    )
    unassigned = [s for s in shards if s["state"] != "STARTED"]
    if unassigned:
        print(f"unassigned / non-started shards ({len(unassigned)}):")
        for s in unassigned:
            reason = s.get("unassigned.reason", "")
            print(
                f"  {s['index']}[{s['shard']}] {s['prirep']} "
                f"{s['state']} {reason}"
            )
    else:
        print("all shards STARTED")

    # Simple DBA-style alerting.
    print("-" * 60)
    if status == "red":
        print("ALERT: cluster is RED. Primary shards missing.")
    elif health["unassigned_shards"] > 0:
        print(
            f"WARNING: {health['unassigned_shards']} unassigned shard(s)."
        )
    elif status == "green":
        print("OK: cluster is healthy.")


if __name__ == "__main__":
    main()
