#!/usr/bin/env python
"""Fetch cluster health and print a human-readable summary.

This wraps GET /_cluster/health and translates the raw numbers into a
short report a DBA can read at a glance, including a plain-English
explanation of what the current green/yellow/red status means.
"""

from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

STATUS_MEANING = {
    "green": (
        "All primary and replica shards are allocated. The cluster is "
        "fully operational with full redundancy."
    ),
    "yellow": (
        "All primary shards are allocated, but one or more REPLICA shards "
        "are not. Your data is fully available, but you have reduced "
        "redundancy. Common on single-node clusters where replicas cannot "
        "be placed on a different node."
    ),
    "red": (
        "At least one PRIMARY shard is not allocated. Some data is missing "
        "or unavailable. This is an emergency: investigate immediately."
    ),
}


def main() -> None:
    """Print a human summary of the current cluster health."""
    health = es.cluster.health()

    status = health["status"]
    print("=" * 60)
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
    print(
        "max task wait (ms):     "
        f"{health.get('task_max_waiting_in_queue_millis', 0)}"
    )

    print("-" * 60)
    # Simple DBA-style alerting heuristics.
    if status == "red":
        print("ALERT: cluster is RED. Primary shards missing.")
    elif health["unassigned_shards"] > 0:
        print(
            f"WARNING: {health['unassigned_shards']} unassigned shard(s). "
            "Run the allocation explain script to find out why."
        )
    elif status == "green":
        print("OK: cluster is healthy.")


if __name__ == "__main__":
    main()
