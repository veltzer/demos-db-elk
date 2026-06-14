# Capacity Planning and Disk Management in Elasticsearch

## Objective

Learn the disk-side of running Elasticsearch as a DBA: where storage goes,
how the disk watermarks change cluster behaviour as nodes fill up, how to
recover from the classic flood-stage read-only incident, how to find the
fields and segments that waste space, and how to forecast when you will run
out of disk.

## Overview

Disk is the resource that most often takes an Elasticsearch cluster down, and
it usually fails in a predictable, preventable way. Elasticsearch reacts to a
filling disk in three stages (the *watermarks*), and at the last stage it
makes indices read-only to protect the node — which surfaces to applications
as failing writes. A DBA needs to recognise the symptoms, clear the block
safely, and plan capacity so it never happens again.

This exercise covers:

- Reading disk usage per node and per index
- The low / high / flood-stage watermarks and how to view and change them
- Reproducing and recovering from the flood-stage read-only block (a runbook)
- The `_disk_usage` API to find which fields cost the most storage
- Segments, `_forcemerge`, and when merging saves space
- A simple storage forecaster (days-until-full)
- Allocation filtering and awareness for hot/warm tiering

## Prerequisites

- Python 3.x with modules: `elasticsearch`, `faker`
- Elasticsearch running on <http://localhost:9200> with security disabled
- See the [`00_install`](../00_install/exercise.md) exercise if you have not
  set it up yet
- Install required modules:

```bash
pip install elasticsearch faker
```

## Part 1: Generate Sample Data

Load an index with enough data that the disk and forecast scripts have real
numbers to report.

See [`01_load_sample_data.py`](./01_load_sample_data.py)

## Part 2: Where Is My Disk Going

The first thing a DBA looks at during a capacity review or a "disk full"
incident: usage per data node, the largest indices, and per-index store size.

See [`02_disk_usage_overview.sh`](./02_disk_usage_overview.sh)

## Part 3: Disk Watermarks

The three thresholds that govern how Elasticsearch reacts as a node fills up.
This script shows how to view the current (and default) values and how to
change them with a cluster settings update.

See [`03_disk_watermarks.sh`](./03_disk_watermarks.sh)

The defaults are:

- **low** (85%) — stop allocating *new* shards to this node
- **high** (90%) — actively relocate shards *away* from this node
- **flood_stage** (95%) — mark indices with a shard on this node read-only

## Part 4: The Flood-Stage Incident

### 4.1 Reproduce the Read-Only Block

Rather than actually filling the disk, apply the exact block Elasticsearch
applies at flood stage so you can rehearse the recovery safely.

See [`04_simulate_flood_stage.sh`](./04_simulate_flood_stage.sh)

### 4.2 The Recovery Runbook

The step-by-step runbook for "my indices have gone read-only and writes are
failing": confirm the cause, free disk *first*, then clear the block.

See [`05_flood_stage_runbook.sh`](./05_flood_stage_runbook.sh)

## Part 5: Find the Expensive Fields

The `_disk_usage` API reads the on-disk Lucene structures and reports, per
field, how many bytes go to the inverted index, doc values, stored fields and
points. It is the answer to "what should I stop indexing to shrink this
index?".

See [`06_disk_usage_analysis.py`](./06_disk_usage_analysis.py)

## Part 6: Segments and Force Merge

Too many small segments waste disk and RAM and slow search. Inspect segment
counts and decide whether a force merge is worthwhile (usually only on
read-only or old time-based indices).

See [`07_segments_and_forcemerge.sh`](./07_segments_and_forcemerge.sh)

## Part 7: Forecast Days Until Full

Given current store size, doc count, and an estimated ingest rate, project
growth per day and how many days of free disk remain.

See [`08_capacity_forecast.py`](./08_capacity_forecast.py)

## Part 8: Steering Shards (Hot/Warm Tiering)

Allocation filtering and awareness let you control *where* shards land — the
foundation of hot/warm/cold tiering and of rack/zone fault tolerance.

See [`09_allocation_filtering.sh`](./09_allocation_filtering.sh)

## Discussion

- **Watermarks are per node, not per cluster.** A single hot node crossing
  flood stage makes *every* index with a shard on it read-only, even if the
  rest of the cluster is empty. Balance shards before you add disk.
- **The flood-stage block does not always clear itself.** On older versions
  you must clear `index.blocks.read_only_allow_delete` by hand *after* freeing
  disk. Never clear it first — you will just flood again.
- **Cheapest storage wins are mapping choices.** High-cardinality analyzed
  text fields dominate the inverted index. Switching display-only fields to
  `keyword`/`index: false`, disabling `_source` only when safe, and using the
  `best_compression` codec are the big levers — `_disk_usage` tells you which.
- **Force merge is destructive of resources.** `max_num_segments=1` rewrites
  the whole shard and is expensive; only run it on indices that will no longer
  be written to.
- **Forecast from real rates, not guesses.** A capacity plan is store bytes
  per document times documents per day. Measure both from the live cluster.

## Challenge Exercises

1. Lower the flood-stage watermark to a value just above your current usage,
   write a document, and watch the read-only block appear — then recover.
1. Use `_disk_usage` to find the most expensive field in the sample index,
   change its mapping, reindex, and measure the store-size difference.
1. Set `index.codec` to `best_compression` on a new index, load the same data,
   and compare store sizes against the default.
1. Tag a node with `node.attr.data: warm` and use index allocation filtering
   to pin an old index onto it.

## Next Steps

1. Combine watermark monitoring with the alerting exercise
   ([`25_monitoring_alerting`](../25_monitoring_alerting/exercise.md))
1. Automate hot/warm tiering with ILM — see
   [`18_index_lifecycle_management`](../18_index_lifecycle_management/)
1. Plan shard sizing up front
   ([`17_shard_management`](../17_shard_management/exercise.md))
