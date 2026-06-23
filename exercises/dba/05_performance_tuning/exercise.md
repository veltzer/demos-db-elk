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

See [`01_generate_load.py`](./01_generate_load.py)

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

See [`02_jvm_heap_gc.py`](./02_jvm_heap_gc.py)

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

See [`02b_set_heap_notes.sh`](./02b_set_heap_notes.sh)

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

Elasticsearch does not spawn a new thread for every request. Instead it
routes work to a small set of fixed-size thread pools, one per kind of
operation (`write` for indexing, `search` for queries, `get` for
single-document fetches, and so on). Each pool has a bounded queue in
front of it. This design protects the node: a fixed number of threads
means CPU and memory use stay predictable no matter how many clients
pile on at once.

See [`03_thread_pools.py`](./03_thread_pools.py)

This reads the data behind
`GET /_cat/thread_pool?v&h=node_name,name,active,queue,rejected` and
flags any pool with rejections, focusing on `write` and `search`.

What's happening: the script reports `active` (threads currently
working), `queue` (tasks waiting), and `rejected` (tasks dropped). The
key concept is what a rejection means. When every thread is busy *and*
the queue is full, Elasticsearch does not slow the request down, it
refuses it outright with an `es_rejected_execution_exception` (HTTP
429). The work is dropped, not delayed. The instinct to "just make the
queue bigger" is the classic trap: a longer queue only buries the
latency and delays the moment you notice the cluster is overloaded. The
real fixes are to reduce client concurrency, batch more sensibly with
retry-and-backoff, or scale out across more nodes and shards.

## Part 3: Caches

Caching is how Elasticsearch turns a repeated query into a near-instant
response. There are three caches a DBA cares about, and they cache very
different things at very different layers. Understanding which cache a
query can use is the difference between guessing and tuning.

### Step 3.1: Inspect Cache Usage

See [`04_caches.py`](./04_caches.py)

This reads
`GET /_nodes/stats/indices/query_cache,request_cache,fielddata` and
reports each cache's size, evictions, and hit ratio, with a warning if
fielddata is non-zero.

What's happening: the hit ratio is the headline number. A ratio near
zero after warm-up means the cache is not earning its memory, usually
because queries are not repetitive or the cache is too small (look at
the eviction count: high evictions relative to size mean entries are
being pushed out before they can be reused). The two good caches here
are the query cache (filter bitsets, shared across the node) and the
request cache (whole responses for `size=0` aggregation and count
requests). The dangerous one is fielddata: it should usually stay tiny.
A non-zero fielddata size is the script's red flag that something is
sorting or aggregating on a `text` field, which builds an expensive
in-memory structure that can exhaust the heap. The fix is to aggregate
on a `keyword` field instead, exactly like the mapping in Part 0.

### Step 3.2: Clear Caches to Re-Measure

See [`04b_clear_cache.sh`](./04b_clear_cache.sh)

This calls `POST /<index>/_cache/clear` so you can compare cold vs warm
behaviour. Re-run `04_caches.py` afterwards to watch the caches warm up.

Why this matters: clearing caches is a measurement trick, not
maintenance. In normal operation Elasticsearch manages eviction itself,
and clearing a warm cache only throws away work and makes the next
queries slow. The value here is experimental: clear, run a query once
(a cold miss), run it again (a warm hit), and watch the hit ratio climb
in `04_caches.py`. That before-and-after contrast is what teaches you
how much a given workload actually benefits from caching.

## Part 4: Circuit Breakers

A circuit breaker is the JVM's seatbelt. The danger it guards against is
an `OutOfMemoryError`, which does not fail one request, it crashes the
entire node. To prevent that, Elasticsearch estimates how much memory a
request will need *before* allocating it. If that estimate would push
the node past a configured limit, the breaker trips and the single
request fails with a `CircuitBreakingException` (HTTP 429). Sacrificing
one request to keep the node alive is always the right trade.

See [`05_circuit_breakers.py`](./05_circuit_breakers.py)

This reads `GET /_nodes/stats/breaker` and prints each breaker's limit,
estimated usage, and trip count, explaining the parent, fielddata, and
request breakers.

What's happening: there is a hierarchy of breakers. The `parent`
breaker caps total usage across all the others (around 95% of heap by
default, backed by a real-memory breaker that watches actual heap), and
the child breakers (`fielddata`, `request`, `in_flight_requests`) cap
their own subsystems. The `tripped` column is the one that matters: any
non-zero count means a request was refused. Reading *which* breaker
tripped points straight at the cause. A fielddata trip means text-field
aggregation; a request trip means an oversized aggregation; a tripping
parent breaker means the node is simply short on heap, which loops you
back to Part 1.

## Part 5: Slow Logs

The statistics in Parts 1 to 4 tell you a node is unhealthy but not
*which requests* are causing the pain. Slow logs close that gap. When a
query or an index operation takes longer than a threshold you set,
Elasticsearch writes the full request source to a dedicated log file.
This is the only built-in way to catch the specific offending requests,
complete with the query that produced them.

See [`06_enable_slowlogs.sh`](./06_enable_slowlogs.sh)

This issues `PUT /<index>/_settings` to enable the search and indexing
slow logs with sensible warn/info/debug/trace thresholds, documents
where the slow-log lines land, and then **demonstrates** them: it forces
a couple of slow queries and prints the resulting slow-log lines so you
see the mechanism end to end rather than just enabling it.

What's happening: the thresholds are tiered (warn, info, debug, trace)
so you can keep the warn tier quiet for genuine emergencies while a
lower tier captures merely-sluggish requests. They are dynamic index
settings, meaning they take effect immediately with no restart, and
they apply at the shard level. Note the two search phases: the "query"
phase is the per-shard search that finds matching documents, while the
"fetch" phase loads the matched documents' contents, so they get
separate thresholds. Setting any tier to `-1` turns it off.

Where the lines land depends on the log4j2 slow-log appender. On a
classic package install it is a rolling **file**
(`<cluster>_index_search_slowlog.json` and the indexing equivalent) in
the Elasticsearch logs directory, commonly `/var/log/elasticsearch/`. In
the official **Docker** image this exercise uses, the slow-log appender
is a *console* appender, so the lines go to the container's stdout and
you read them with `docker logs elasticsearch` instead of tailing a file.

The demo at the end of the script handles both the "make it fire" and
the "show me the line" halves. A query against a 20,000-document demo
index finishes in a millisecond or two, far below the 500ms trace
threshold, so on an idle laptop nothing would ever be logged. The script
therefore (1) temporarily drops the trace threshold to `0ms` so that
*any* query is logged (the reliable way to see the mechanism), and also
(2) runs a genuinely expensive query, a leading-wildcard regexp
(`.*london.*`) that cannot use the inverted index and must scan every
term. It restores the 500ms threshold afterwards, then pulls the most
recent search slow-log lines out of `docker logs`. Each line carries the
offending query under `elasticsearch.slowlog.source` and its time under
`elasticsearch.slowlog.took`, which is exactly how you catch the
specific requests hurting a cluster.

## Part 6: Profile a Slow Query

Once a slow log has identified a problem query, you need to know *why*
it is slow. The Profile API breaks a single query into its component
parts and measures the time each one spends, per shard. It is the
difference between knowing a query is slow and knowing that, say, a
`range` clause on an un-indexed field is eating ninety percent of the
time.

See [`07_profile_slow_query.py`](./07_profile_slow_query.py)

This runs a query with `profile: true` and attributes time to each query
component on each shard. (Field-index timing is covered in the
[`02_query_performance`](../../shared/02_query_performance/exercise.md)
exercise, so this is intentionally brief.) It also points at the
`_search` with `"explain": true` companion for per-document score
attribution.

What's happening: a `bool` query is a tree of clauses, and the profile
output mirrors that tree. The script reports each query component's
total time plus its top sub-operations from the `breakdown` map, and
the collector time spent gathering and scoring matches on the shard.
Two companion ideas are worth separating. Profile answers "where did
the *time* go", measured in nanoseconds. The `explain` option answers a
different question, "why did this document match and how was its score
computed". Timing is a performance tool; explain is a relevance tool.

## Part 7: Write-Path Tuning

Everything so far has been about reading and serving data. Writing data
has its own performance levers, and they all trade safety or freshness
for throughput. Two settings dominate. The first controls how often new
documents become searchable; the second controls how aggressively
Elasticsearch protects writes against a crash. Both make sense to relax
during a big bulk load and to restore immediately afterwards.

See [`08_tune_write_settings.sh`](./08_tune_write_settings.sh)

This raises `index.refresh_interval` and sets
`index.translog.durability=async` for a write-heavy bulk load, explains
the trade-offs, and shows how to restore the safe near-real-time
defaults afterwards.

What's happening: a refresh is what makes newly indexed documents
visible to search, and each refresh creates a new Lucene segment. The
default of one second is why Elasticsearch feels near-real-time, but
during a bulk load it generates a flood of tiny segments that must
later be merged, burning CPU and disk. Raising the interval to 30s, or
disabling it with `-1` and refreshing manually at the end, removes that
overhead. Separately, the translog is a write-ahead log: by default it
is flushed to disk on every acknowledged write (`durability: request`),
which is durable but slow. Switching to `async` flushes only every few
seconds, trading a small window of crash-loss for throughput. That is
only safe when you can re-drive the lost writes from the source, which
is exactly the situation in a re-runnable bulk load.

Common pitfall: forgetting to revert. These are relaxed-safety settings
for a load window, not steady-state defaults. Always restore
`refresh_interval: 1s` and `durability: request` once the load is done,
which is why the script prints the restore commands for you.

## Part 8: Consolidated Perf Snapshot

See [`09_perf_snapshot.py`](./09_perf_snapshot.py)

This consolidates heap percent, thread-pool rejections, breaker trips,
and cache hit ratios into a single report with `[OK]` / `[WARN]` /
`[ALERT]` tags. It exits non-zero when anything is in ALERT, so it can
be wired into cron or a CI health gate.

Why this matters: the individual scripts are for investigation, but
nobody runs ten scripts by hand every morning. This snapshot is the
"one screen you glance at" version, pulling the four key signals into a
single pass over the stats APIs. The detail to notice is the non-zero
exit code on ALERT. A process exit code is the universal language of
automation: a cron job, a monitoring agent, or a CI pipeline can run
this script and react to its exit status without parsing any output.
That is how a diagnostic becomes a health gate.

## Files

- [`01_generate_load.py`](./01_generate_load.py) - create index and load (run first)
- [`02_jvm_heap_gc.py`](./02_jvm_heap_gc.py) - heap, pools, and GC report
- [`02b_set_heap_notes.sh`](./02b_set_heap_notes.sh) - how to set heap
- [`03_thread_pools.py`](./03_thread_pools.py) - thread-pool rejections
- [`04_caches.py`](./04_caches.py) - cache sizes and hit ratios
- [`04b_clear_cache.sh`](./04b_clear_cache.sh) - clear caches
- [`05_circuit_breakers.py`](./05_circuit_breakers.py) - breaker trips
- [`06_enable_slowlogs.sh`](./06_enable_slowlogs.sh) - enable slow logs
- [`07_profile_slow_query.py`](./07_profile_slow_query.py) - profile API
- [`08_tune_write_settings.sh`](./08_tune_write_settings.sh) - write tuning
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
runtime. Watch the GC numbers from `02_jvm_heap_gc.py`: frequent or long
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
  free. A non-zero fielddata size in `04_caches.py` is worth a look.

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

Thresholds apply at the shard level and are dynamic (no restart). Where
the lines land depends on the log4j2 appender: on a package install they
go to the rolling `*_search_slowlog.json` and `*_indexing_slowlog.json`
files in the Elasticsearch logs directory (commonly
`/var/log/elasticsearch/`), while in the official Docker image the
appender is a console appender, so they go to the container's stdout
(read them with `docker logs elasticsearch`). Set a threshold to `-1` to
disable that tier.

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
   `05_circuit_breakers.py`. Then fix it with a keyword sub-field.
1. **Provoke rejections.** Hammer the cluster with many concurrent bulk
   or search requests and catch the rejections in `03_thread_pools.py`.
1. **Measure write tuning.** Time a bulk load with default settings vs
   `refresh_interval: -1` + `durability: async`, then compare.
1. **Compare cold vs warm caches.** Run `04b_clear_cache.sh`, then a
   query, then `04_caches.py` repeatedly to watch hit ratios climb.

## Next Steps

1. Wire `09_perf_snapshot.py` into a cron job and alert on its non-zero
   exit status.
1. Correlate slow-log entries with the profile output from
   `07_profile_slow_query.py` to fix specific slow queries.
1. Repeat the heap/GC and breaker analysis on a real multi-node cluster.
1. Explore index sorting, force-merge after bulk loads, and shard sizing
   ([`01_shard_management`](../01_shard_management/exercise.md)) as further
   performance levers.
