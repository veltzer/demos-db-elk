# Index Lifecycle Management (ILM) in Elasticsearch

This exercise teaches the day-to-day DBA skill of managing time-series indices
automatically: rolling them over as they grow, ageing them through cheaper
storage tiers, and deleting them once their retention has elapsed. You will
build the same pipeline two ways — the classic rollover-alias approach and the
modern data stream approach — and then watch an index transition through every
lifecycle phase in a single short session.

## Overview

For logs, metrics and other append-only data you do not want one giant,
ever-growing index. Instead you let Elasticsearch:

- write into a "hot" index and **roll over** to a fresh one on size/age/count
- move ageing indices to **warm** then **cold** tiers (shrink, force-merge,
  read-only) to reclaim resources
- **delete** them automatically once retention is reached

ILM is the engine that drives all of this from a single declarative policy.

Why does this matter? An index is not free. Every shard holds open file
handles, consumes heap for its data structures, and is scanned by the cluster
on every recovery. A single index that grows without bound eventually has
shards too large to relocate, too slow to query, and impossible to delete in
part. The whole point of ILM is to keep individual indices small, predictable
and disposable, and to let Elasticsearch — not a human with a calendar — decide
when each one has done its job.

The mental model to hold onto: you do not manage one index, you manage a
*series* of indices behind a single stable name. New data always lands in the
youngest one; the older ones quietly age, get optimised, and are eventually
dropped.

The exercise includes:

- An ILM policy with hot / warm / cold / delete phases (shell and Python)
- Reusable component templates and a composable index template
- Bootstrapping a managed index with a write alias (classic approach)
- Creating a data stream (modern approach)
- Triggering a manual rollover and inspecting the new backing index
- Inspecting and controlling ILM (`_ilm/explain`, status, start/stop, move)
- A Python script that lets you actually see the phase transitions
- A cleanup script that removes every object created

## Objective

By the end you will be able to design a retention strategy, express it as an
ILM policy, attach it to indices via templates, and operate it (force
rollovers, diagnose stuck indices, pause the lifecycle for maintenance).

## Prerequisites

- Python 3.x with the `elasticsearch` module
- Elasticsearch running on <http://localhost:9200> with security disabled
  (plain HTTP)
- Install the required module:

```bash
pip install elasticsearch
```

Elasticsearch should be reachable on `localhost:9200`. See the
[`00_install`](../../shared/00_install/exercise.md) exercise if you have not
set it up yet. This exercise targets Elasticsearch 8.x / 9.x (data streams and
composable
index templates).

## Files

- `01_create_ilm_policy.sh` - Create the `logs-policy` ILM policy with
  hot/warm/cold/delete phases (curl)
- `02_create_ilm_policy.py` - The same policy created via the Python client
- `03_create_templates.sh` - Component templates plus a composable index
  template that attaches the policy and a rollover alias
- `04_bootstrap_rollover_alias.sh` - Bootstrap the first managed index with a
  write alias (`is_write_index`) - the classic approach
- `05_create_data_stream.sh` - Create a data stream - the modern approach
- `06_manual_rollover.sh` - Force a rollover and observe the new backing index
- `07_inspect_ilm.sh` - Inspect and control ILM: `_ilm/explain`, `_ilm/status`,
  `_ilm/start|stop`, `_ilm/move`
- `08_watch_transitions.py` - Speed up ILM and watch an index advance through
  every phase in minutes
- `09_cleanup.sh` - Remove every policy, template, index and data stream

## Quick Start

### Step 1: Create the ILM Policy

The policy is the heart of everything else. It is a declarative document that
names the phases an index passes through and the actions to take in each one.
Critically, the policy is just stored configuration: creating it changes
nothing on its own. Nothing happens until an index is *attached* to the policy
(in Step 2 via a template). Think of the policy as a recipe and the template
as the thing that hands that recipe to every new index.

The script defines four phases (hot, warm, cold, delete) with the rollover
trigger in hot and a `min_age` on each later phase. Read the inline comments:
they explain that `min_age` is counted from rollover, not creation, so a `7d`
warm age means "seven days after this index stopped being written".

See [`01_create_ilm_policy.sh`](./01_create_ilm_policy.sh)

The Python equivalent builds the identical policy from a dictionary, which is
useful when the retention value is environment-specific:

See [`02_create_ilm_policy.py`](./02_create_ilm_policy.py)

### Step 2: Create the Templates

A composable index template is assembled from reusable component templates and
is what actually attaches the ILM policy and rollover alias to any index whose
name matches the pattern:

What is happening under the hood: an index template never touches any existing
index. It is a standing instruction that says "when an index whose name matches
`logs-*` is created, give it these settings and mappings". The two settings
that do the real work here are `index.lifecycle.name` (which policy governs
this index) and `index.lifecycle.rollover_alias` (which alias the rollover
action should advance). Because both are baked into the template, every new
backing index inherits them automatically — you never have to remember to set
them by hand.

The split into *component* templates plus one *composable* template is about
reuse: settings and mappings live in their own fragments so several index
templates can share them. The `priority` field matters because several
templates can match the same name; Elasticsearch picks the highest priority.
This is why Step 3b uses a higher priority to override this one for its more
specific pattern — a common source of confusion when a new index silently picks
up the "wrong" settings.

See [`03_create_templates.sh`](./03_create_templates.sh)

### Step 3a: Bootstrap a Managed Index (Classic Rollover Alias)

With a rollover alias you create the first index yourself, suffixed `-000001`,
and mark it as the write index for the alias:

Two details here are easy to get wrong and worth understanding. First, the
`-000001` suffix is not cosmetic: rollover works by parsing the trailing number
and incrementing it, so the very first index must end in a zero-padded integer
or rollover has nothing to count from. Second, `is_write_index: true` tells the
alias which of its (eventually many) indices should receive new writes. An
alias can point at several indices for reads, but exactly one must be the write
target — forgetting this flag is the classic rollover-alias mistake, and writes
will be rejected as ambiguous.

See [`04_bootstrap_rollover_alias.sh`](./04_bootstrap_rollover_alias.sh)

### Step 3b: Create a Data Stream (Modern Approach)

A data stream hides the backing indices entirely and needs no
`is_write_index`. It requires a template containing a `data_stream` object and
documents that carry an `@timestamp`:

Why is the bootstrap step gone? A data stream manages its own write index, so
there is no manual `-000001` to create and no write flag to set. Elasticsearch
generates hidden backing indices named `.ds-...` and always writes to the
newest one. The trade-off is that data streams are strictly append-only: you
can add documents but not update or delete individual ones in place, which is
exactly the right contract for logs and metrics but wrong for mutable data.

Note also the deliberate `priority` of 600 in the script. Its pattern
`logs-stream*` overlaps the `logs-*` pattern from Step 2, and the higher
priority guarantees the data-stream template wins for names starting with
`logs-stream`. The required `@timestamp` is how a data stream orders and
time-partitions its backing indices, so a document without one is rejected.

See [`05_create_data_stream.sh`](./05_create_data_stream.sh)

### Step 4: Trigger a Rollover

Roll the write index forward on demand and watch the backing index list grow
from `logs-000001` to `logs-000002`:

A manual rollover does by hand exactly what ILM does for you on a schedule: it
creates a fresh backing index, makes it the new write target, and leaves the
old one frozen for reads. Two subtleties the script demonstrates. It first
indexes a document because a rollover on an empty index is, by default, a no-op
— Elasticsearch will not leave you with a string of empty indices. And calling
`_rollover` with an empty body forces an *unconditional* roll; passing
`conditions` instead rolls only if a threshold is met, which is precisely the
check ILM performs each poll. Doing it manually here makes that otherwise
invisible machinery concrete.

See [`06_manual_rollover.sh`](./06_manual_rollover.sh)

### Step 5: Inspect and Control ILM

See [`07_inspect_ilm.sh`](./07_inspect_ilm.sh)

### Step 6: Watch the Lifecycle Transitions

This is the payoff. The script lowers the cluster ILM poll interval to 10
seconds, creates a policy whose phases advance after a minute or two, and polls
`_ilm/explain` so you can watch an index walk hot -> warm -> cold -> delete:

See [`08_watch_transitions.py`](./08_watch_transitions.py)

```bash
./08_watch_transitions.py
```

### Step 7: Clean Up

See [`09_cleanup.sh`](./09_cleanup.sh)

## Discussion

### The hot / warm / cold / delete model

ILM models the life of a time-series index as an ordered sequence of phases.
An index always starts in `hot` and moves forward; it never moves backward.

1. **Hot** - the index is actively written and queried. The only phase that may
   contain a `rollover` action. Put it on your fastest hardware.
1. **Warm** - the index is no longer written but is still queried. Typical
   actions: `shrink` (fewer shards), `forcemerge` (one segment, smaller and
   faster), `allocate` (move to warm nodes), `readonly`.
1. **Cold** - rarely queried. Reduce replicas, mark read-only, allocate to
   cheap, dense, slow storage. (Searchable snapshots can push this even
   cheaper on a licensed cluster; the freeze action of older versions is now
   effectively "make it read-only and cold".)
1. **Delete** - once retention is reached, the index is removed.

The `min_age` of each phase is measured from the moment the index **rolled
over** (not from when it was created), so retention is counted from when the
index stopped receiving writes. `set_priority` controls recovery order after a
restart: hot indices recover first.

### Rollover vs fixed time-based indices

An older pattern names indices by date (`logs-2026.06.14`) and relies on the
client to write to today's index. That ties index size to a calendar period,
which is fragile: a traffic spike produces a huge index and a quiet day a tiny
one.

**Rollover** decouples index boundaries from the calendar. You write to a
stable target (an alias or data stream) and Elasticsearch starts a new backing
index when a condition is met:

- `max_primary_shard_size` - the recommended primary trigger; keeps shards in
  the healthy tens-of-GB range regardless of traffic
- `max_age` - an upper bound so even quiet indices eventually roll
- `max_docs` - a document-count cap

Rollover only happens while ILM polls the index (default every 10 minutes) and
the index is non-empty, so an index can briefly exceed its target before it
rolls.

### Data streams vs rollover aliases

Both give you a single name to write to that is backed by a rolling series of
indices. The differences:

| | Rollover alias | Data stream |
| --- | --- | --- |
| Bootstrap | you create `-000001` + `is_write_index` | created automatically |
| Backing index names | you choose the prefix | hidden `.ds-...` indices |
| `@timestamp` required | no | **yes** |
| Writes | index or update any doc | append-only (no in-place update) |
| Recommended for | mixed/updatable data | pure append-only time series |

For new log/metric pipelines prefer **data streams**: they are simpler, less
error-prone (no forgetting `is_write_index`), and the default in modern
Elastic tooling. Keep rollover aliases when you must update existing documents
or need to control the backing index names.

### Retention strategy

Retention is a business decision about cost vs availability:

- Decide how long data must be **queryable** (drives the warm/cold cut-offs)
  and how long it must be **kept at all** (drives the delete `min_age`).
- Size shards via `max_primary_shard_size` rather than a doc count guess; aim
  for shards in the tens of GB.
- Push old data to cheaper tiers before deleting it, rather than keeping
  everything hot.
- ILM acts only as fast as `indices.lifecycle.poll_interval` (default `10m`).
  Lowering it (as `08_watch_transitions.py` does) makes transitions snappier
  but adds master overhead — keep it modest in production.

## Challenge

1. Modify `01_create_ilm_policy.sh` to roll over on `max_age` of 1 day and a
   `max_primary_shard_size` of 20gb, then re-create the policy and confirm with
   `_ilm/explain`.
1. Convert the rollover-alias pipeline to a pure data stream and write a small
   producer (reuse `stream_data.py` from the
   [`13_streaming_ingestion`](../../shared/13_streaming_ingestion/exercise.md)
   exercise)
   that appends an `@timestamp` per document.
1. Use `_ilm/stop`, manually `_ilm/move` an index from `hot` to `warm`, then
   `_ilm/start` and watch it continue from `_ilm/explain`.
1. Add an `allocate` step that requires a node attribute (for example
   `data: warm`) and observe what happens on a single-node cluster where no
   such node exists (hint: the index gets "stuck" — read `_ilm/explain`).

## Next Steps

1. Combine ILM with snapshots (see
   [`19_snapshot_restore`](../19_snapshot_restore/exercise.md)) for a
   snapshot-then-delete retention policy.
1. Explore searchable snapshots for the cold/frozen tier on a licensed cluster.
1. Wire ILM into a real ingestion pipeline and alert on stuck indices.
1. Review how index templates and aliases interact in
   [`21_index_templates_aliases`](../21_index_templates_aliases/exercise.md).
