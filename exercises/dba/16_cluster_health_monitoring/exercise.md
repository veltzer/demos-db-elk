# Cluster and Node Health Monitoring

## Objective

Learn how a database administrator monitors the health of an
Elasticsearch cluster: reading cluster status, inspecting nodes and
shards, diagnosing unassigned shards, watching JVM heap, GC and
thread-pool pressure, capturing hot threads, and building a
consolidated health dashboard.

By the end you will be able to answer the three questions a DBA is
paged about most often:

1. Is the cluster green, yellow, or red, and why?
1. Which node or shard is the problem?
1. Is the cluster under resource pressure (heap, CPU, disk, rejections)?

## Why monitoring matters

Elasticsearch is a distributed system: your data is split into shards,
each shard is copied into replicas, and those pieces are spread across
nodes. This design buys scalability and fault tolerance, but it also
means failures are partial and quiet. A node can drop out, a disk can
fill up, or a shard can fail to allocate while the rest of the cluster
keeps answering queries. Nothing crashes loudly; the cluster simply
becomes less safe or slower. Monitoring is how you make these partial,
silent failures visible before they turn into data loss or an outage.

Every tool in this exercise is a different lens on the same underlying
cluster state. The cluster status tells you whether shards are placed;
node stats tell you whether the machines are healthy; hot threads tell
you what work is consuming a node; tasks tell you what the cluster is
busy doing. A skilled DBA learns to move quickly from the high-level
signal (the status color) down to the specific root cause.

## Overview

The scripts in this exercise wrap the core Elasticsearch monitoring
APIs:

- `GET /_cluster/health` - overall and per-index/per-shard status
- `GET /_cat/health` and `GET /_cat/nodes` - compact tabular views
- `GET /_cat/shards` - shard listing and unassigned-shard hunting
- `GET /_cluster/allocation/explain` - why a shard is unassigned
- `GET /_nodes/stats` - JVM heap, GC, thread-pool rejections per node
- `GET /_nodes/hot_threads` - what a busy node is actually doing
- `GET /_cluster/pending_tasks` and `GET /_tasks` - queued and running
  work

## Prerequisites

- Python 3.x with the `elasticsearch` module
- Elasticsearch running on <http://localhost:9200> with security
  disabled (plain HTTP, no auth)
- Install the Python client:

```bash
pip install elasticsearch
```

If Elasticsearch is not installed or running, see the install exercise
in [`../00_install`](../../shared/00_install).

Make the scripts executable once:

```bash
chmod +x *.sh *.py
```

## Files and Steps

### Step 1: Overall cluster health

Check the cluster status and break it down per index and per shard.

See [`01_cluster_health.sh`](./01_cluster_health.sh)

Why this matters: `GET /_cluster/health` is the first call any DBA
makes. It returns a single status color plus a set of counters that
summarize the whole cluster. Under the hood the master node tracks the
state of every shard; this endpoint aggregates that state into one
answer. The `level` parameter controls how far down you drill: the
default gives the cluster-wide color, `level=indices` shows which index
is unhealthy, and `level=shards` pinpoints the exact shard. The habit
to build is starting broad and narrowing only as far as you need to.

Then get a human-readable interpretation of the status, including the
plain-English meaning of green/yellow/red and simple alert heuristics.

See [`02_interpret_health.py`](./02_interpret_health.py)

What is happening: this script reads the same health document but
translates the raw counters into a short report. The fields worth
understanding are `active_primary_shards` (how many primaries are
placed), `active_shards` (primaries plus replicas), and
`unassigned_shards` (the count that explains a yellow or red color).
The `active_shards_percent_as_number` field is the quickest gauge of
all: it is 100% on a fully placed cluster and dips while shards are
initializing or relocating. Building a human summary on top of a raw
API is itself a useful pattern, because it forces you to decide which
numbers actually drive a decision.

### Step 2: Nodes and compact health views

Use the `_cat` APIs to see roles, heap, CPU, load and disk per node.

See [`03_cat_nodes_and_health.sh`](./03_cat_nodes_and_health.sh)

Why this matters: the `_cat` APIs return plain tabular text instead of
JSON, which makes them perfect for a quick human glance in a terminal.
They expose the same data as the JSON stats APIs but pre-formatted into
columns. Add `?v` to get a header row and `?h=col1,col2` to choose
exactly the columns you care about. The status color tells you a shard
is misplaced; `_cat/nodes` tells you whether a machine is the reason,
by showing each node's roles, heap, CPU, OS load, and disk usage side
by side. The `master` column marks the one elected master node with an
asterisk, which matters because cluster-state changes flow through it.
The `_cat/allocation` view adds shard count and disk usage per node,
which is exactly what you need when chasing a disk-watermark problem.

### Step 3: Shards and unassigned shards

List every shard and filter down to UNASSIGNED ones - the shards that
make a cluster yellow or red.

See [`04_cat_shards.sh`](./04_cat_shards.sh)

What is happening: a shard is the unit Elasticsearch actually places on
a node, so the shard list is the ground truth behind the status color.
Each row shows whether the shard is a primary (`p`) or replica (`r`)
and its `state`. A healthy shard is STARTED; INITIALIZING and
RELOCATING mean the cluster is in transition and usually recovers on
its own; UNASSIGNED means the shard has nowhere to live. The script
filters down to UNASSIGNED shards and shows their `unassigned.reason`,
because those are the shards that explain a yellow or red color and the
ones you must act on. Seeing transition states is also useful: a few
INITIALIZING shards after a restart are normal, but shards stuck in
transition for a long time are a signal that something is wrong.

### Step 4: Explain an unassigned shard

When a shard is unassigned, this is the tool that tells you exactly why
(disk watermark, allocation filtering, missing node, throttling, ...).

See [`05_allocation_explain.py`](./05_allocation_explain.py)

### Step 5: Per-node JVM, GC and thread-pool stats

Pull heap used %, GC counts/time, and thread-pool rejection counts into
a per-node table.

See [`06_node_stats.py`](./06_node_stats.py)

### Step 6: Hot threads

Capture what the busiest threads on each node are doing - the first
thing to run when a node is pegged at high CPU.

See [`07_hot_threads.sh`](./07_hot_threads.sh)

### Step 7: Pending and running tasks

Show queued cluster-state changes and live long-running tasks (which can
be cancelled).

See [`08_pending_and_tasks.py`](./08_pending_and_tasks.py)

### Step 8: The consolidated dashboard

Poll several of the above APIs and print a single one-screen status
report. Pass an interval in seconds for a live, refreshing view.

See [`09_health_dashboard.py`](./09_health_dashboard.py)

## Discussion: What Each Metric Means

### Cluster status (green / yellow / red)

- **green**: all primary and replica shards are allocated. Full
  redundancy.
- **yellow**: all primaries are allocated, but some replicas are not.
  Data is fully available but redundancy is reduced. On a single-node
  cluster this is expected and normal, because a replica can never be
  placed on the same node as its primary.
- **red**: at least one PRIMARY shard is not allocated. Some data is
  unavailable. This is an incident - act immediately.

`active_shards_percent_as_number` is a quick health gauge: 100% on a
green cluster, lower while shards initialize or relocate.

### Nodes (`_cat/nodes`)

- **node.role**: which roles a node holds (m=master-eligible, d=data,
  i=ingest, and others). The `master` column marks the elected master
  with `*`.
- **heap.percent**: JVM heap used. Watch for sustained values above
  **75%** - this is where GC pressure and instability begin.
- **cpu / load_1m / load_5m / load_15m**: OS-level load. Sustained high
  load with high CPU points at heavy query or indexing work.
- **disk.used_percent**: disk pressure. Elasticsearch enforces disk
  watermarks (default low 85%, high 90%, flood-stage 95%). Crossing the
  high watermark stops new shards from being allocated to the node;
  flood stage makes indices read-only.

### Shards (`_cat/shards`)

Every shard has a `state`: STARTED (healthy), INITIALIZING or
RELOCATING (in transition), or UNASSIGNED. Unassigned shards carry an
`unassigned.reason` (for example `NODE_LEFT`, `ALLOCATION_FAILED`,
`CLUSTER_RECOVERED`, `INDEX_CREATED`). Persistent unassigned shards are
what you must explain and fix.

### Allocation explain

`/_cluster/allocation/explain` returns a per-node decision list. Each
decider can answer yes, no, or THROTTLE. The common no reasons a DBA
sees are:

- **disk threshold**: the node is over the high watermark.
- **same shard / awareness**: a replica cannot sit on the same node or
  zone as its primary (the single-node yellow case).
- **allocation filtering**: index settings explicitly exclude the node.
- **max retries**: allocation failed repeatedly; retry with
  `POST /_cluster/reroute?retry_failed=true`.

### Node stats (heap, GC, rejections)

- **JVM heap used %**: the most important memory signal. Above 75%
  sustained is a warning; near 100% with frequent old-GC means the node
  is in trouble.
- **GC**: rising **old**-generation collection counts and long
  collection times indicate memory pressure. Young GC is normal and
  frequent.
- **Thread-pool rejections**: any non-zero `rejected` count on the
  `search`, `write`, `bulk` or `get` pools means the cluster could not
  keep up and dropped work. This is a strong signal that the cluster is
  overloaded or under-provisioned.

### Hot threads

`/_nodes/hot_threads` samples stack traces of the busiest threads. It
tells you whether high CPU is from search, indexing, merges, GC, or
script execution - turning "node 2 is at 100% CPU" into an actionable
root cause.

### Pending and running tasks

- **pending_tasks**: cluster-state changes queued on the master
  (mapping updates, allocation decisions). A consistently growing queue
  means the master is a bottleneck - often caused by too many indices
  or rapid mapping changes.
- **_tasks**: every running task. Long-running searches, reindexes or
  snapshots show up here and can be cancelled with
  `POST /_tasks/<task_id>/_cancel`.

## Suggested Alert Thresholds for a DBA

- cluster status **red** -> page immediately.
- cluster status **yellow** on a multi-node cluster for more than a few
  minutes -> investigate.
- unassigned shards > 0 (steady state) -> run allocation explain.
- JVM heap > 75% sustained -> investigate; > 85% -> alert.
- disk used > 85% (high watermark) -> alert; > 90% -> urgent.
- any thread-pool rejections -> alert.
- pending cluster-state tasks consistently > 0 -> investigate master.

## Challenge Exercises

1. **Force a yellow cluster**: create an index with one replica on a
   single-node cluster, then use `04_cat_shards.sh` and
   `05_allocation_explain.py` to confirm the replica is unassigned and
   read the exact decider that blocked it.
1. **Fix it without adding a node**: set
   `index.number_of_replicas` to `0` on that index and watch the
   cluster return to green via `02_interpret_health.py`.
1. **Generate thread-pool pressure**: fire many concurrent searches or a
   large bulk load and watch for rejections in `06_node_stats.py`.
1. **Watch a live dashboard**: run
   `09_health_dashboard.py 2` in one terminal while you create indices,
   change replica counts, or run a reindex in another, and watch the
   numbers move.
1. **Cancel a task**: start a slow reindex, find it with
   `08_pending_and_tasks.py`, and cancel it with the task management
   API.

## Next Steps

1. Wire these checks into a real alerting tool (cron + thresholds, or a
   Watcher/alerting stack).
1. Compare these manual checks against Kibana's Stack Monitoring views.
1. Continue to the shard management and index lifecycle exercises to
   learn how to remediate the problems you can now detect.
