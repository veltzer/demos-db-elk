#!/usr/bin/env python
"""Explain why a shard is (un)assigned.

POSTs to GET /_cluster/allocation/explain and pretty-prints the decision.
When run with no arguments, Elasticsearch picks an arbitrary unassigned
shard to explain. You can also point it at a specific shard by editing
the request body below.

This is the single best tool for answering "why is my cluster yellow/red?"
"""

from elasticsearch import Elasticsearch
from elasticsearch import ApiError

es = Elasticsearch("http://localhost:9200")


def explain(body=None) -> None:
    """Run an allocation explain request and summarize the result."""
    try:
        # With no body, ES chooses an arbitrary unassigned shard. If
        # everything is assigned it returns a 400, which we handle below.
        result = es.cluster.allocation_explain(body=body or {})
    except ApiError as exc:
        # The full error text lives in the structured body (reason field),
        # not in str(exc), which only carries the short reason. Inspect both
        # so we reliably catch the "everything is assigned" case.
        error = (getattr(exc, "body", None) or {}).get("error", {})
        reason = error.get("reason", "") if isinstance(error, dict) else ""
        haystack = f"{reason} {exc}"
        if "unable to find any unassigned shards" in haystack:
            print(
                "No unassigned shards to explain. The cluster has nothing "
                "stuck. To explain an ASSIGNED shard, set the index/shard/"
                "primary fields in the request body."
            )
            return
        raise

    idx = result.get("index")
    shard = result.get("shard")
    primary = result.get("primary")
    kind = "primary" if primary else "replica"
    print("=" * 60)
    print(f"shard: {idx}[{shard}] ({kind})")
    print(f"current_state: {result.get('current_state')}")
    print("=" * 60)

    unassigned = result.get("unassigned_info")
    if unassigned:
        print("--- why it is unassigned ---")
        print(f"reason:     {unassigned.get('reason')}")
        print(f"since:      {unassigned.get('at')}")
        details = unassigned.get("details")
        if details:
            print(f"details:    {details}")
        print(
            "last_allocation_status: "
            f"{unassigned.get('last_allocation_status')}"
        )

    decision = result.get("can_allocate")
    if decision:
        print(f"--- can_allocate: {decision} ---")

    explanation = result.get("allocate_explanation")
    if explanation:
        print(explanation)

    # Per-node decisions tell you exactly which allocation rule blocked
    # the shard on each node (disk watermark, awareness, filtering, ...).
    for node in result.get("node_allocation_decisions", []):
        name = node.get("node_name")
        node_decision = node.get("node_decision")
        print(f"\nnode: {name} -> {node_decision}")
        for d in node.get("deciders", []):
            if d.get("decision") in ("NO", "THROTTLE"):
                print(f"  [{d['decision']}] {d['decider']}: {d['explanation']}")


if __name__ == "__main__":
    explain()
