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

A useful mental model before you start: Elasticsearch stores data as
immutable Lucene *segments* grouped into *shards*, and shards are placed
on *data nodes*. Almost every disk question in this exercise comes back to
those three layers — how big the segments are, which fields inside them
cost the most bytes, which node a shard lives on, and how full that node's
filesystem is. The disk watermarks are simply percentages of a node's
filesystem, so the unit Elasticsearch actually reacts to is "percent of
disk used on one node", not "total cluster storage".

## Prerequisites

- Python 3.x with modules: `elasticsearch`, `faker`
- Elasticsearch running on <http://localhost:9200> with security disabled
- See the [`00_install`](../../shared/00_install/exercise.md) exercise if you
  have not set it up yet
- Install required modules:

```bash
pip install elasticsearch faker
```

## Part 1: Generate Sample Data

Load an index with enough data that the disk and forecast scripts have real
numbers to report.

**Why this matters:** disk and capacity tooling is only meaningful against
a real store size. An empty index reports a few kilobytes of overhead, so
the watermark, `_disk_usage`, and forecast numbers would all be noise. The
loader generates around 100,000 fake event documents (timestamps, log
levels, hostnames, IPs, free-text messages) so the index reaches tens of
megabytes — large enough that per-field byte costs and growth rates become
visible. Note the variety of field types: the free-text `message` field
and high-cardinality strings like `user_agent` are deliberately included
because, as you will see in Part 5, those are usually the fields that
dominate disk usage.

After the bulk load the script calls a *refresh*. A refresh flushes the
in-memory buffer into a searchable segment; until that happens the new
documents are indexed but not yet visible to the `_cat` and `_stats` APIs
the later parts rely on. This is the same refresh mechanism that produces
new segments in Part 6.

See [`01_load_sample_data.py`](./01_load_sample_data.py)

## Part 2: Where Is My Disk Going

The first thing a DBA looks at during a capacity review or a "disk full"
incident: usage per data node, the largest indices, and per-index store size.

**What's happening:** the script moves from coarse to fine. It starts with
`_cat/allocation`, which reports per data node how many shards a node holds
and how much of its filesystem is used. The `disk.percent` column is the
exact number the watermarks are compared against, so this is your early
warning gauge. It then lists indices by store size with `_cat/indices` so
you know *which* index to act on, and finally drills into one index with
`_stats/store`.

A subtle but important distinction appears in that last view: the total
`store.size` includes replica copies, while `pri.store.size` counts only
the primaries. The gap between them is the price you pay for your
replication factor — a one-replica index uses roughly twice the disk of
its raw data. The script also passes `bytes=gb` so every index reports in
the same unit; without a fixed unit a text sort would place "9mb" after
"10gb" and mislead you about what is actually largest.

See [`02_disk_usage_overview.sh`](./02_disk_usage_overview.sh)

## Part 3: Disk Watermarks

The three thresholds that govern how Elasticsearch reacts as a node fills up.
This script shows how to view the current (and default) values and how to
change them with a cluster settings update.

**Why the watermarks exist:** Elasticsearch never wants a node to actually
run out of disk, because a full disk corrupts in-flight writes and can
crash the node. The watermarks are a graduated defence that kicks in
earlier and earlier as a node fills, each stage more aggressive than the
last, ending in a hard write block that keeps the node alive at the cost of
rejecting writes.

When you read the settings, notice the script passes
`include_defaults=true`. Most Elasticsearch settings are invisible until
you override them, so without this flag you would only see watermarks you
have explicitly changed — and on a fresh cluster that is nothing. The flag
makes the built-in defaults visible so you can confirm what is actually in
force.

The script then sets the watermarks as *transient* settings. Transient
settings are held only in cluster state and are lost on a full cluster
restart; *persistent* settings survive restarts and are written to disk.
For a real, lasting policy change you would use persistent; transient is
fine for a temporary tweak or a rehearsal like this one. Reverting a
setting to `null` removes your override and restores the default — this is
the standard pattern for "undo" throughout these scripts.

See [`03_disk_watermarks.sh`](./03_disk_watermarks.sh)

The defaults are:

- **low** (85%) — stop allocating *new* shards to this node
- **high** (90%) — actively relocate shards *away* from this node
- **flood_stage** (95%) — mark indices with a shard on this node read-only

You can express each threshold either as a percentage of disk used (as
above) or as an absolute amount of free space, such as `50gb`. On very
large disks the percentage form can be dangerous: 5% of a 4 TB disk is
200 GB still free at flood stage, which may be far more headroom than you
need, while 5% of a small disk is almost nothing. Big-disk clusters often
switch to absolute values for exactly this reason.

## Part 4: The Flood-Stage Incident

### 4.1 Reproduce the Read-Only Block

Rather than actually filling the disk, apply the exact block Elasticsearch
applies at flood stage so you can rehearse the recovery safely.

**What's happening:** at flood stage Elasticsearch sets
`index.blocks.read_only_allow_delete: true` on every affected index. This
script sets that same flag by hand, so the index ends up in precisely the
state a real flood would produce — without you having to fill a disk. The
"allow delete" part of the name is deliberate: the block forbids writes and
mapping changes but still permits deletes, so you can free space by
dropping data even while blocked.

The script then attempts a write, which fails with a
`cluster_block_exception` (HTTP 429). The error body it prints is exactly
what your application logs would show during a real incident, so learning
to recognise it here is the point of the exercise. The script intentionally
does not abort on that failure so you can read the rejection and continue.

See [`04_simulate_flood_stage.sh`](./04_simulate_flood_stage.sh)

### 4.2 The Recovery Runbook

The step-by-step runbook for "my indices have gone read-only and writes are
failing": confirm the cause, free disk *first*, then clear the block.

**Why the order matters:** the single most common mistake during this
incident is to clear the read-only block first because it looks like the
problem. But the block is a *symptom*; the cause is a full disk. Clear the
block before freeing space and writes resume, the disk fills again within
minutes, and the node re-triggers flood stage — you have made the outage
longer. The runbook therefore enforces the order: detect, free disk, then
unblock.

Reading the steps in order:

- **Step 1 (detect)** queries the per-index block setting and then sweeps
  the whole cluster for any index showing `read_only`, because in a real
  flood every index with a shard on the full node is blocked at once, not
  just the one you noticed.
- **Step 2 (free disk)** is the actual fix. In production this means
  deleting old indices, moving data to a cheaper tier, or adding capacity.
  The demo illustrates the cheapest win, a force merge that expunges
  deleted documents (see Part 6 for what that reclaims).
- **Step 3 (clear the block)** sets the flag back to `null` only after disk
  is recovered. On older Elasticsearch versions this block does not lift
  itself automatically, which is exactly why a manual clear step exists.
- **Step 4 (verify)** writes a document to confirm the index accepts writes
  again, closing the loop.

See [`05_flood_stage_runbook.sh`](./05_flood_stage_runbook.sh)

## Part 5: Find the Expensive Fields

The `_disk_usage` API reads the on-disk Lucene structures and reports, per
field, how many bytes go to the inverted index, doc values, stored fields and
points. It is the answer to "what should I stop indexing to shrink this
index?".

**Understanding the breakdown:** a single field can occupy disk in several
independent ways, and `_disk_usage` separates them so you know which lever
to pull. The four columns map directly to Lucene data structures:

- **inverted index** — the searchable term index built for analyzed text
  and keywords. High-cardinality and free-text fields dominate here. If a
  field is stored only for display and never searched, set `index: false`
  to drop this cost entirely.
- **doc values** — a columnar copy of a field used for sorting,
  aggregating, and scripting. If you never sort or aggregate on a field,
  `doc_values: false` reclaims this.
- **stored fields** — the original values kept for retrieval, largely the
  `_source` document.
- **points** — the data structure for numeric and date range queries.

Because the API physically scans every segment on disk, it is genuinely
expensive, so Elasticsearch refuses to run it unless you pass
`run_expensive_tasks=true`. That flag is mandatory and is the script's way
of acknowledging the cost; do not run this on a busy production index
during peak load without thinking about it. In the sample data, expect the
analyzed `message` and high-cardinality `user_agent`/`url` fields to top
the list — which is the lesson: mapping choices, not raw document count,
are usually where the disk goes.

See [`06_disk_usage_analysis.py`](./06_disk_usage_analysis.py)

## Part 6: Segments and Force Merge

Too many small segments waste disk and RAM and slow search. Inspect segment
counts and decide whether a force merge is worthwhile (usually only on
read-only or old time-based indices).

**What a segment is:** a shard is not one file but a collection of
immutable Lucene segments. Every refresh can create a new small segment,
and Elasticsearch merges them together in the background over time. Two
things make segments waste space. First, each segment carries fixed
overhead, so many tiny segments cost more disk and heap than a few large
ones. Second, when a document is updated or deleted it is not removed in
place — it is marked as deleted in its segment and continues to occupy disk
until a merge rewrites that segment without it. The `docs.deleted` column
shows exactly this dead weight.

A *force merge* rewrites a shard's segments into fewer (or one), dropping
deleted documents and the per-segment overhead along the way. The script
demonstrates two forms: `only_expunge_deletes` (cheaper, just removes the
tombstoned documents) and `max_num_segments=1` (collapses everything into a
single segment, the smallest and fastest-to-search result).

**The critical pitfall:** force merge is expensive and one-directional in
intent. Run `max_num_segments=1` only on an index that will no longer be
written to — such as a previous day's time-based index. On a hot,
still-ingesting index the merge fights a losing battle as new segments keep
appearing, wasting large amounts of I/O. The segment-count checks before
and after the merge let you confirm the effect.

See [`07_segments_and_forcemerge.sh`](./07_segments_and_forcemerge.sh)

## Part 7: Forecast Days Until Full

Given current store size, doc count, and an estimated ingest rate, project
growth per day and how many days of free disk remain.

**The model behind the forecast:** the whole projection rests on one
measured ratio — bytes per document, computed as the index's store size
divided by its document count. Multiply that by your expected documents per
day and you have growth per day; divide remaining free disk by that growth
and you have days until full. The strength of this approach is that the
bytes-per-document figure is read from the *live* index, so it already
reflects your real mappings, replicas, and compression rather than a guess.

**Why it uses the tightest node:** the script finds the data node with the
*least* free disk and forecasts against that one. This is deliberate. A
cluster does not fill evenly; it effectively "fills" at the rate of its
fullest node, because a single node crossing flood stage blocks writes to
every index with a shard there (see the Discussion). Forecasting against
total cluster free space would be dangerously optimistic. The script also
skips the pseudo-rows `_cat/allocation` emits for unassigned shards, since
those carry no disk figures.

The one number you must supply honestly is the ingest rate. In production
you would derive it from real traffic — for example the document-count
difference between two consecutive days of a time-based index — rather than
estimating. A forecast is only as good as that input.

See [`08_capacity_forecast.py`](./08_capacity_forecast.py)

## Part 8: Steering Shards (Hot/Warm Tiering)

Allocation filtering and awareness let you control *where* shards land — the
foundation of hot/warm/cold tiering and of rack/zone fault tolerance.

**Why a DBA cares about placement:** capacity is not only "how much disk"
but "which disk". You want hot, frequently-searched indices on fast nodes
and large old indices on cheaper nodes with bigger but slower disks.
Steering shards to the right hardware is how you get both performance and
cost control. The script shows the two mechanisms involved.

The first is per-index *allocation filtering*. Nodes are tagged with custom
attributes (for example `node.attr.data: warm` in `elasticsearch.yml`), and
an index setting such as `index.routing.allocation.require.data: warm`
tells Elasticsearch to place that index only on matching nodes. On a
single-node dev cluster with no such tag this is harmless — the setting is
recorded but the shard has nowhere else to go, so it stays put. In
production this same setting is how you migrate an aging index onto the
warm tier.

The second is cluster-wide allocation *awareness*. Setting
`cluster.routing.allocation.awareness.attributes` to something like `zone`
tells Elasticsearch to spread a shard's primary and replicas across
distinct values of that attribute, so that losing one zone or rack cannot
take down every copy of a shard. Note this is set with `persistent`, since
a fault-tolerance policy should survive restarts, whereas the per-index
filter is a property of the index itself. Every change in the script is
reverted at the end so the cluster is left as it was found.

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
   ([`08_monitoring_alerting`](../08_monitoring_alerting/exercise.md))
1. Automate hot/warm tiering with ILM — see
   [`02_index_lifecycle_management`](../02_index_lifecycle_management/)
1. Plan shard sizing up front
   ([`01_shard_management`](../01_shard_management/exercise.md))
