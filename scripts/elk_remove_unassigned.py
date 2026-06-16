#!/usr/bin/env python
"""Remove / clear unassigned shards from an Elasticsearch cluster.

An unassigned shard keeps the cluster yellow (replica) or red (primary).
There are two cases and they are handled very differently:

  * Unassigned REPLICA: usually a single-node cluster that has nowhere to
    place the copy. The safe fix is to stop asking for that replica, i.e.
    set number_of_replicas=0 on the affected index. No data is lost.

  * Unassigned PRIMARY: the actual data for that shard is not available.
    There is nothing to "remove" without losing data. The only way to make
    the shard go away is to force-allocate an EMPTY primary, which DISCARDS
    whatever was in it. This is destructive and is only done when you pass
    --force-empty-primary.

By default this script does the safe thing (drops unassigned replicas) and
merely REPORTS any unassigned primaries.

Set ES_URL to target a non-default host (default http://localhost:9200).

Usage:
    ./elk_remove_unassigned.py                      # drop unassigned replicas
    ./elk_remove_unassigned.py --force-empty-primary  # also wipe stuck primaries
"""

import os
import sys

from elasticsearch import Elasticsearch

ES_URL = os.environ.get("ES_URL", "http://localhost:9200")


def unassigned_shards(es):
    """Return the list of currently unassigned shards via _cat/shards."""
    shards = es.cat.shards(
        h="index,shard,prirep,state,unassigned.reason", format="json"
    )
    return [s for s in shards if s.get("state") == "UNASSIGNED"]


def main() -> None:
    """Clear unassigned replicas; optionally force-empty stuck primaries."""
    force_empty = "--force-empty-primary" in sys.argv[1:]

    es = Elasticsearch(ES_URL)
    print(f"target: {ES_URL}")

    shards = unassigned_shards(es)
    if not shards:
        print("no unassigned shards. nothing to do.")
        return

    # Split into replicas (p/r flag == "r") and primaries ("p").
    replicas = [s for s in shards if s.get("prirep") == "r"]
    primaries = [s for s in shards if s.get("prirep") == "p"]

    print(
        f"found {len(shards)} unassigned shard(s): "
        f"{len(primaries)} primary, {len(replicas)} replica"
    )

    # --- replicas: drop them by setting number_of_replicas=0 per index ---
    replica_indices = sorted({s["index"] for s in replicas})
    for index in replica_indices:
        print(f"  dropping unassigned replicas on '{index}' (replicas=0)")
        es.indices.put_settings(
            index=index, body={"index": {"number_of_replicas": 0}}
        )

    # Nudge the cluster to retry anything that previously failed allocation.
    if replica_indices:
        es.cluster.reroute(retry_failed=True)

    # --- primaries: report, and only wipe if explicitly forced ---
    for s in primaries:
        index, shard = s["index"], int(s["shard"])
        reason = s.get("unassigned.reason", "")
        if not force_empty:
            print(
                f"  PRIMARY {index}[{shard}] is unassigned ({reason}). "
                "Data is unavailable. Re-run with --force-empty-primary to "
                "allocate an EMPTY primary (DESTROYS this shard's data)."
            )
            continue

        print(
            f"  FORCING empty primary for {index}[{shard}] -- "
            "this discards the shard's data."
        )
        # accept_data_loss must be true; ES refuses otherwise.
        es.cluster.reroute(
            body={
                "commands": [
                    {
                        "allocate_empty_primary": {
                            "index": index,
                            "shard": shard,
                            "node": _any_node(es),
                            "accept_data_loss": True,
                        }
                    }
                ]
            }
        )

    # --- final state ---
    remaining = unassigned_shards(es)
    print("-" * 60)
    if remaining:
        print(f"{len(remaining)} unassigned shard(s) still present:")
        for s in remaining:
            print(
                f"  {s['index']}[{s['shard']}] {s['prirep']} "
                f"{s.get('unassigned.reason', '')}"
            )
    else:
        print("all unassigned shards cleared.")

    health = es.cluster.health()
    print(
        f"cluster status: {health['status'].upper()}  "
        f"unassigned_shards: {health['unassigned_shards']}"
    )


def _any_node(es):
    """Pick an arbitrary node name to host a force-allocated empty primary."""
    nodes = es.cat.nodes(h="name", format="json")
    return nodes[0]["name"]


if __name__ == "__main__":
    main()
