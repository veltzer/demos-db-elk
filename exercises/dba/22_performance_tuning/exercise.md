# Performance Tuning and Diagnostics in Elasticsearch

## Objective

Learn the operational, cluster-side knobs a DBA uses to keep
Elasticsearch fast and healthy: JVM heap and garbage collection, thread
pools, the query/request/fielddata caches, circuit breakers, slow logs,
and write-path tuning (refresh interval and translog durability). You
will run scripts that read live node statistics, flag problems with
simple WARN/OK heuristics, and apply (and revert) tuning settings.

This exercise is operational and complements exercise
`04_query_performance`, which covers field indexing and per-query
timing. Here we look at the cluster underneath the queries.

The mental model to carry through this exercise: a query is only as
fast as the node serving it. Most "slow Elasticsearch" complaints are
not about a bad query at all, they are about a node that is short on
heap, thrashing its garbage collector, dropping requests because its
thread pools are saturated, or being protected by a tripped circuit
breaker. The scripts here read the same live statistics APIs a real
DBA watches, so you learn to diagnose the cluster, not just the query.

## Overview

The exercise covers:

1. JVM heap usage, memory pools, and garbage-collection activity, plus
   the heap-sizing rules of thumb.
1. Thread pools and what a "rejection" really means.
1. The query cache, request cache, and the dangers of fielddata on text
   fields.
1. Circuit breakers (parent / fielddata / request) and trip counts.
1. Search and indexing slow logs.
1. Profiling a single slow query with `profile: true`.
1. Refresh-interval and translog-durability tuning for write-heavy
   workloads.
1. A consolidated "perf snapshot" report with WARN/OK flags.

## Prerequisites

- Python 3.x with modules: `elasticsearch`, and optionally `faker`
  (used by the load generator; it falls back to canned data if missing).
- Elasticsearch running on <http://localhost:9200> with security
  disabled (plain HTTP). See [`../00_install`](../../shared/00_install).
- Install the required modules:

```bash
pip install elasticsearch faker
```

Accurate for Elasticsearch 8.x and 9.x.

## Part 0: Generate Some Load to Measure

Most stats are zero on an idle cluster. Create the demo index, bulk-load
documents, and warm the caches first:

See [`06_generate_load.py`](./06_generate_load.py)

This creates the `perf_demo` index with a `keyword` field (safe for
aggregation) and a `text` field (for search), loads 20,000 documents,
and runs repeated filter + aggregation queries so the caches and thread
pools show real activity.

Why this matters: every counter in this exercise (cache hits, thread
pool activity, GC time) is cumulative and starts at zero. Without
traffic, the inspection scripts would report a clean but meaningless
"all zero" picture. The script deliberately runs the *same* filtered
aggregation twenty times, because a cache only proves itself on the
second and later runs. The first run is a cache miss that populates the
cache; the repeats turn into cache hits, which is exactly the warm vs
cold behaviour you measure in Part 3.

The mapping is the first lesson in disguise. `department` and `city`
are `keyword`, `bio` is `text`. That choice decides what you can safely
aggregate on later: keyword fields get on-disk `doc_values` for free,
while aggregating on a text field would force expensive in-memory
fielddata. Keep this mapping in mind when you reach the caches and
breakers below.

## Part 1: JVM Heap and Garbage Collection

Elasticsearch runs on the Java Virtual Machine, and the JVM heap is the
single most important resource a DBA watches. Java is a garbage-
collected language: instead of freeing memory explicitly, it
periodically pauses to reclaim objects that are no longer referenced.
The heap is split into a young generation (short-lived objects, cheap
to collect) and an old generation (long-lived objects, expensive to
collect). When the old generation fills up, the JVM must do a slow,
sometimes stop-the-world collection that freezes the node. Watching
heap usage and GC time tells you how close a node is to that cliff.

### Step 1.1: Inspect Heap and GC per Node

See [`01_jvm_heap_gc.py`](./01_jvm_heap_gc.py)

This reads `GET /_nodes/stats/jvm` and prints heap used percent, the
young/survivor/old memory pool sizes, and the cumulative GC counts and
times per node, with a heap-pressure flag.

What's happening under the hood: the script flags a node at 75% heap as
a warning and 85% as an alert. These thresholds matter because the old
generation does not get collected continuously; it builds up until a
major collection fires. A node sitting at 85% is doing frequent,
lengthy old-generation collections just to stay afloat, and a single
large aggregation can tip it into a circuit-breaker trip (Part 4). The
GC numbers are cumulative since node start, so what you watch for is the
*rate of change* between two runs: a fast-climbing old-GC time is the
clearest early warning of sustained heap pressure.

### Step 1.2: How to Set the Heap

See [`01b_set_heap_notes.sh`](./01b_set_heap_notes.sh)

This documents the two supported ways to set heap (a
`jvm.options.d/*.options` drop-in file, or the `ES_JAVA_OPTS`
environment variable) and shows the heap your node currently runs with.

A common pitfall: bigger heap is not always better. Two rules govern
the size and the Discussion section below explains why. The short
version is that the heap should be at most half of physical RAM (the
other half feeds the operating-system file cache that Lucene depends
on) and should stay under about 31GB (so the JVM can keep using
compressed object pointers). The drop-in file is the preferred method
because it survives upgrades and lives alongside the rest of the JVM
configuration rather than in a shell environment that is easy to lose.

## Part 2: Thread Pools

See [`02_thread_pools.py`](./02_thread_pools.py)

This reads the data behind
`GET /_cat/thread_pool?v&h=node_name,name,active,queue,rejected` and
flags any pool with rejections, focusing on `write` and `search`.

## Part 3: Caches

### Step 3.1: Inspect Cache Usage

See [`03_caches.py`](./03_caches.py)

This reads
`GET /_nodes/stats/indices/query_cache,request_cache,fielddata` and
reports each cache's size, evictions, and hit ratio, with a warning if
fielddata is non-zero.

### Step 3.2: Clear Caches to Re-Measure

See [`03b_clear_cache.sh`](./03b_clear_cache.sh)

This calls `POST /<index>/_cache/clear` so you can compare cold vs warm
behaviour. Re-run `03_caches.py` afterwards to watch the caches warm up.

## Part 4: Circuit Breakers

See [`04_circuit_breakers.py`](./04_circuit_breakers.py)

This reads `GET /_nodes/stats/breaker` and prints each breaker's limit,
estimated usage, and trip count, explaining the parent, fielddata, and
request breakers.

## Part 5: Slow Logs

See [`05_enable_slowlogs.sh`](./05_enable_slowlogs.sh)

This issues `PUT /<index>/_settings` to enable the search and indexing
slow logs with sensible warn/info/debug/trace thresholds, and documents
where the slow-log files land.

## Part 6: Profile a Slow Query

See [`08_profile_slow_query.py`](./08_profile_slow_query.py)

This runs a query with `profile: true` and attributes time to each query
component on each shard. (Field-index timing is covered in exercise 04,
so this is intentionally brief.) It also points at the
`_search` with `"explain": true` companion for per-document score
attribution.

## Part 7: Write-Path Tuning

See [`07_tune_write_settings.sh`](./07_tune_write_settings.sh)

This raises `index.refresh_interval` and sets
`index.translog.durability=async` for a write-heavy bulk load, explains
the trade-offs, and shows how to restore the safe near-real-time
defaults afterwards.

## Part 8: Consolidated Perf Snapshot

See [`09_perf_snapshot.py`](./09_perf_snapshot.py)

This consolidates heap percent, thread-pool rejections, breaker trips,
and cache hit ratios into a single report with `[OK]` / `[WARN]` /
`[ALERT]` tags. It exits non-zero when anything is in ALERT, so it can
be wired into cron or a CI health gate.

## Files

- [`01_jvm_heap_gc.py`](./01_jvm_heap_gc.py) - heap, pools, and GC report
- [`01b_set_heap_notes.sh`](./01b_set_heap_notes.sh) - how to set heap
- [`02_thread_pools.py`](./02_thread_pools.py) - thread-pool rejections
- [`03_caches.py`](./03_caches.py) - cache sizes and hit ratios
- [`03b_clear_cache.sh`](./03b_clear_cache.sh) - clear caches
- [`04_circuit_breakers.py`](./04_circuit_breakers.py) - breaker trips
- [`05_enable_slowlogs.sh`](./05_enable_slowlogs.sh) - enable slow logs
- [`06_generate_load.py`](./06_generate_load.py) - create index and load
- [`07_tune_write_settings.sh`](./07_tune_write_settings.sh) - write tuning
- [`08_profile_slow_query.py`](./08_profile_slow_query.py) - profile API
- [`09_perf_snapshot.py`](./09_perf_snapshot.py) - consolidated snapshot

## Discussion

### Heap Sizing and GC

The JVM heap is where Elasticsearch keeps most of its working memory.
Two rules dominate sizing:

1. **Heap <= 50% of physical RAM.** The other half is left to the
   operating-system filesystem cache, which Lucene relies on to serve
   searches quickly. Giving Elasticsearch a huge heap and starving the
   file cache usually makes searches slower, not faster.
1. **Heap under ~31GB.** Above roughly 32GB the JVM can no longer use
   compressed ordinary object pointers (compressed oops). A 32GB heap
   can therefore hold less usable data than a 30GB heap, while also
   producing longer GC pauses. If you need more memory, add nodes rather
   than growing one heap past ~31GB.

Also set `-Xms` equal to `-Xmx` so the JVM never resizes the heap at
runtime. Watch the GC numbers from `01_jvm_heap_gc.py`: frequent or long
**old-generation** (old / "Old Gen") collections are the warning sign of
sustained heap pressure. A node that sits above 85% heap and does long
old-GC pauses is one expensive aggregation away from a breaker trip.

### Thread Pools

Each pool has a fixed thread count and a bounded queue. When both are
full, new tasks are **rejected** with `es_rejected_execution_exception`
(HTTP 429). A rejection means work was dropped, not merely slowed. The
fix is almost never "make the queue bigger" (that just adds latency and
hides the problem). Instead:

- Reduce client concurrency and batch size; use retry-with-backoff
  (the official bulk helpers do this for you).
- Scale out: more shards/nodes spread the work.
- For search, cut expensive queries/aggregations and the number of
  shards each request touches.

### Caches

- **Query cache** caches filter-clause bitsets and is shared across the
  node. Repeated filters benefit greatly. Use `filter` context for
  non-scoring clauses to take advantage of it.
- **Request cache** caches the full response of `size=0` requests
  (typically aggregations and counts). Toggle per index with
  `index.requests.cache.enable` (default `true`).
- **Fielddata** is the dangerous one. Sorting or aggregating on a
  **text** field forces an in-memory fielddata structure that can blow
  the heap. never enable fielddata on text fields; instead aggregate or
  sort on a `keyword` sub-field, which uses on-disk `doc_values` for
  free. A non-zero fielddata size in `03_caches.py` is worth a look.

Clearing caches with `POST /<index>/_cache/clear` is a diagnostic tool
for measuring cold-vs-warm behaviour, not a routine maintenance task.

### Circuit Breakers

Circuit breakers are the JVM's seatbelt. Before a request can allocate
enough memory to OOM the node, the breaker trips and that one request
fails with a `CircuitBreakingException` (HTTP 429). The **parent**
breaker caps total usage (default ~95% of heap, backed by the real-memory
breaker that watches actual heap). The **fielddata** and **request**
breakers cap their respective subsystems. Any non-zero `tripped` count
means a request was sacrificed to keep the node alive: investigate heap
pressure, fielddata on text fields, and oversized aggregations.

### Slow Logs

Slow logs record the individual queries and index operations that exceed
a threshold, in warn/info/debug/trace tiers, including the request
source. Suggested starting thresholds:

- search query: warn `10s`, info `5s`, debug `2s`, trace `500ms`
- search fetch: warn `1s`, info `800ms`
- indexing: warn `10s`, info `5s`, debug `2s`, trace `500ms`

Thresholds apply at the shard level and are dynamic (no restart). Lines
land in the `*_search_slowlog.json` and `*_indexing_slowlog.json` files
in the Elasticsearch logs directory (commonly `/var/log/elasticsearch/`
on a package install). Set a threshold to `-1` to disable that tier.

### Write-Path Tuning

For write-heavy or bulk workloads:

- **`index.refresh_interval`** (default `1s`) controls how often new
  documents become searchable. Each refresh creates a Lucene segment, so
  raising it (e.g. `30s`) or disabling it (`-1`) during a bulk load cuts
  CPU/IO and merge pressure. Trade-off: documents are not searchable
  until the next refresh.
- **`index.translog.durability`** defaults to `request` (fsync the
  translog on every acknowledged write: durable but slower). Setting it
  to `async` fsyncs every `sync_interval` (default `5s`), so a crash can
  lose up to that window of acknowledged writes in exchange for higher
  throughput. Only acceptable when lost writes can be re-driven from the
  source.

Always revert to safe defaults (`refresh_interval: 1s`,
`durability: request`) after the bulk load.

## Challenge Exercises

1. **Force a fielddata trip.** Add a text-only field, aggregate on it
   without a keyword sub-field, and watch the fielddata breaker in
   `04_circuit_breakers.py`. Then fix it with a keyword sub-field.
1. **Provoke rejections.** Hammer the cluster with many concurrent bulk
   or search requests and catch the rejections in `02_thread_pools.py`.
1. **Measure write tuning.** Time a bulk load with default settings vs
   `refresh_interval: -1` + `durability: async`, then compare.
1. **Compare cold vs warm caches.** Run `03b_clear_cache.sh`, then a
   query, then `03_caches.py` repeatedly to watch hit ratios climb.

## Next Steps

1. Wire `09_perf_snapshot.py` into a cron job and alert on its non-zero
   exit status.
1. Correlate slow-log entries with the profile output from
   `08_profile_slow_query.py` to fix specific slow queries.
1. Repeat the heap/GC and breaker analysis on a real multi-node cluster.
1. Explore index sorting, force-merge after bulk loads, and shard sizing
   (exercise 17) as further performance levers.
