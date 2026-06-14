# Shard and Replica Management and Sizing in Elasticsearch

## Objective

Learn how a DBA manages the physical layout of an Elasticsearch index:
choosing the number of primary shards and replicas, inspecting how shards are
distributed, diagnosing the oversharding problem, and reshaping a live index
with the `_shrink`, `_split` and `_forcemerge` APIs. You will also learn how
to investigate unassigned or relocating shards.

## Overview

A shard is a self-contained Lucene index and the unit Elasticsearch uses to
scale and distribute data. Getting the shard count right is one of the most
important and most permanent sizing decisions a DBA makes:

- `number_of_shards` is fixed at index creation. Changing it later requires
  `_shrink`, `_split`, or a full reindex.
- `number_of_replicas` is DYNAMIC and can be changed on a live index.
- Too many tiny shards (oversharding) wastes heap and cluster overhead.
- Too few huge shards (undersharding) slows recovery, search, and balancing.

This exercise walks through the full lifecycle on a sample log index.

## Prerequisites

- Python 3.x with modules: `elasticsearch`, `faker`
- Elasticsearch running on <http://localhost:9200> with security disabled
  (plain HTTP, no auth). See [`../00_install`](../../shared/00_install)
- Install required modules:

```bash
pip install elasticsearch faker
```

Note: several effects (replicas going green, shards balancing across nodes)
are only fully visible on a multi-node cluster. On a single-node dev box the
replicas stay UNASSIGNED and the index sits at `yellow`; this is expected and
the scripts handle it.

## Part 1: Create an Index With Explicit Shard Settings

Create the `logs_sharded` index with 4 primary shards, 1 replica, and a
routing-shard count of 32 (which leaves room to split later).

See [`01_create_index.sh`](./01_create_index.sh)

## Part 2: Load Sample Data

Bulk load fake log documents so the shards have real store size to inspect.

See [`02_load_sample_data.py`](./02_load_sample_data.py)

You can pass a document count, for example
`./02_load_sample_data.py 100000`.

## Part 3: Inspect Shard Distribution

Use the `_cat` APIs to see every shard, its primary/replica role, doc count,
store size, and which node holds it, plus per-node allocation.

See [`03_inspect_shards.sh`](./03_inspect_shards.sh)

## Part 4: Detect Oversharding

Report shard count vs data size for every index and flag shards that are too
small (oversharded) or too large (undersharded) against the 10-50GB target
band.

See [`04_shard_sizing_report.py`](./04_shard_sizing_report.py)

## Part 5: Change Replica Count at Runtime

Raise and lower `number_of_replicas` on the live index and watch cluster
health move between `yellow` and `green`.

See [`05_change_replicas.sh`](./05_change_replicas.sh)

## Part 6: Shrink an Index (Fewer Primaries)

Merge the 4-primary `logs_sharded` into a 2-primary `logs_shrunk`, showing
the full correct procedure: pin shards to one node, make the source
read-only, shrink, then restore write access.

See [`06_shrink_index.sh`](./06_shrink_index.sh)

## Part 7: Split an Index (More Primaries)

Divide the 4-primary `logs_sharded` into an 8-primary `logs_split`, showing
the modern split rules (target must be a multiple of the source and divide
`number_of_routing_shards`).

See [`07_split_index.sh`](./07_split_index.sh)

## Part 8: Force-Merge a Read-Only Index

Merge a finished index down to one segment per shard to reclaim disk and
speed up searches, with before/after segment counts.

See [`08_forcemerge.sh`](./08_forcemerge.sh)

## Part 9: Investigate Allocation

Use `_cluster/allocation/explain` to find out exactly why a shard is
unassigned, and use `_cluster/reroute?retry_failed=true` to retry failed
allocations.

See [`09_allocation_explain.sh`](./09_allocation_explain.sh)

## Discussion: Shard Sizing Best Practices

1. **Target shard size 10-50GB.** This is the sweet spot for search latency
   and recovery time. Time-series/log data often targets the higher end;
   search-heavy data the lower end.
1. **Watch shards per node and per GB of heap.** A common guideline is to
   keep below roughly 20 shards per GB of heap. Every shard carries fixed
   overhead regardless of how little data it holds.
1. **Oversharding is the common failure.** Creating many indices each with
   many primaries (the old default was 5) quickly produces thousands of tiny
   shards that exhaust heap and slow the master node. Prefer fewer primaries
   and use rollover/ILM to roll to a new index by size or age.
1. **Replicas are for redundancy and read scale, not write speed.** More
   replicas means more disk and more indexing work, but more nodes that can
   serve reads and survive a node failure.

### When to use shrink vs split vs forcemerge

1. **`_shrink`** — fix an OVERSHARDED index. Reduces primaries to a factor of
   the original count (4 -> 2 or 1). Requires the index to be read-only and
   all primaries gathered on one node so segments can be hard-linked. Fast
   because it does not re-index data. Use it when shards are far below the
   target size.
1. **`_split`** — fix an UNDERSHARDED index. Increases primaries to a
   multiple of the original count, bounded by `number_of_routing_shards`
   (which is fixed at creation). Requires the index to be read-only. Use it
   when shards have grown well past the target size and you want to spread
   load across more nodes.
1. **`_forcemerge?max_num_segments=1`** — does not change shard count. It
   merges Lucene segments within each shard to reclaim space from deleted
   docs and speed up search. Only run it on indices that will never be
   written again; a single giant segment on an active index cannot be merged
   away later and becomes a liability.
1. **Reindex** — the fallback when none of the above fit (for example, you
   need a shard count that is neither a factor nor a multiple, or you need to
   change the mapping or analysis). It rewrites all data into a fresh index
   and is the most expensive option.

## Cleanup

Remove the indices created by this exercise:

```bash
curl -s -X DELETE "localhost:9200/logs_sharded,logs_shrunk,logs_split"
```

## Challenge Exercises

1. **Find the oversharding limit.** Create 20 indices each with 5 primaries
   and 1 replica, then run the sizing report and `_cat/shards` and observe
   how many tiny shards the cluster now carries.
1. **Round-trip a reshape.** Split `logs_sharded` to 8, then shrink the
   result back to 2, confirming doc counts are preserved at each step.
1. **Trigger a real unassigned shard.** Add allocation filtering that no node
   satisfies, then use `_cluster/allocation/explain` to read the exact
   reason, then remove the filter and watch it recover.
1. **Measure forcemerge payoff.** Delete a large fraction of documents, note
   the store size, force-merge, and measure how much disk is reclaimed.

## Next Steps

1. Combine shard sizing with Index Lifecycle Management (rollover by size).
1. Explore `index.routing.allocation.*` filtering for hot/warm tiers.
1. Tune `cluster.routing.allocation.disk.watermark.*` thresholds.
1. Automate the sizing report to alert when shards drift out of band.
