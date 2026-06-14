# Reindexing and Version Upgrades in Elasticsearch

## Objective

Learn the two related DBA skills of moving data between indices and moving a
cluster between versions: the `_reindex` API in all its forms (basic, async,
mapping change, transformation, conflict handling, parallelism, remote), the
zero-downtime "migrate an index" pattern using an alias, and the rolling
upgrade runbook.

## Overview

Field mappings in Elasticsearch are largely immutable: once `created` is a
`text` field you cannot turn it into a `date` in place. The supported fix is
always the same — create a new index with the correct mapping and copy the
data in with `_reindex`. The same `_reindex` machinery (especially its remote
form) is how you migrate data into a freshly built cluster during a major
upgrade.

Why is `_reindex` a server-side operation at all? Elasticsearch could have
left copying to client tools, but doing it inside the cluster means the data
never leaves the nodes: it reads from the source shards and writes to the
destination shards using the same scroll-and-bulk machinery the engine uses
internally. That is faster and avoids the network round-trip of pulling every
document out to a client and pushing it back. The cost is that a large
reindex consumes cluster resources, which is why throttling and parallelism
(Parts 5) exist as explicit controls.

This exercise covers:

- Basic server-side `_reindex` (a plain copy)
- Asynchronous reindex with task tracking for large indices
- Reindexing to change a field's type — the canonical use case
- Transforming documents in flight with a Painless script and a query filter
- Conflict handling (`conflicts: "proceed"`) and parallelism (`slices`)
- Remote reindex across clusters (and the whitelist requirement)
- An end-to-end zero-downtime "migrate index" script using an alias swap
- The rolling upgrade runbook (one node at a time)

## Prerequisites

- Python 3.x with the `elasticsearch` module
- Elasticsearch running on <http://localhost:9200> with security disabled
- See the [`00_install`](../../shared/00_install/exercise.md) exercise if you
  have not set it up yet
- Install required modules:

```bash
pip install elasticsearch
```

## Part 1: Basic Reindex

Copy every document from a source index into a new destination index — no
mapping change, no transformation, just a server-side copy.

**What's happening:** `_reindex` opens a scroll over the source index, reads
documents in batches, and bulk-indexes them into the destination. With the
default `wait_for_completion=true` the HTTP call blocks and returns a summary
once finished: how many documents were `created`, how long it `took`, and
whether there were `failures`. The destination index must already accept the
documents; if it does not exist, Elasticsearch creates it with dynamically
guessed mappings, which is rarely what you want — that is exactly why the
mapping-change pattern in Part 3 creates the target index first.

**Why this matters:** every other reindex variant in this exercise is this
same copy with one extra ingredient (a query, a script, slices, a remote
source). Getting the plain case right is the foundation. Note the script
seeds `products_v1` with `created` stored as `text`, a deliberately wrong
type that motivates the mapping fix later.

See [`01_basic_reindex.sh`](./01_basic_reindex.sh)

## Part 2: Asynchronous Reindex with Task Tracking

For a large index you do not want to hold the HTTP connection open. Passing
`wait_for_completion=false` returns a task id immediately; poll the Tasks API
to watch progress.

**What's happening:** the reindex still runs server-side, but now in the
background as a tracked task. The response is just `{ "task": "node:number" }`.
You then `GET /_tasks/<id>` to read a live `status` block (counters for
`created`, `total`, `batches`) and a `completed` flag. On a real
multi-million-document copy you would loop on that flag rather than guess when
it is done. The completed task result is stored in a hidden `.tasks` index so
you can fetch the outcome even after the job ends.

**Why this matters:** a blocking reindex that runs for an hour is fragile — a
dropped connection, a proxy timeout, or a closed laptop leaves you unsure
whether it finished. The async form decouples "start the job" from "wait for
the job." It also gives a DBA a way to find work someone else started:
`GET /_tasks?actions=*reindex` lists every running reindex in the cluster, and
a runaway one can be stopped with `POST /_tasks/<id>/_cancel`.

See [`02_async_reindex_task.sh`](./02_async_reindex_task.sh)

## Part 3: Reindex to Change a Field Type

The canonical reason `_reindex` exists. You cannot remap a field in place, so
create a new index with the corrected mapping and reindex into it.

**Why mappings are immutable:** a field's type decides how its values are
turned into the inverted index and other on-disk data structures at index
time. A `text` value is analyzed into tokens; a `date` is stored as a number;
a `keyword` is stored verbatim. Changing the type would invalidate everything
already written, so Elasticsearch refuses. Adding a brand-new field is fine
(nothing on disk to invalidate), but changing an existing one is not.

**What's happening:** the script creates `products_v2` with the corrected
mapping *first* (`created` as `date`, `category` as `keyword`), then reindexes
into it. The destination mapping wins: because the source strings like
`"2024-01-15"` are valid dates, Elasticsearch parses them into the date field
during the copy. The script then proves the change worked by running a date
`range` query — something that only behaves correctly against a real date
field, not a text one.

**Common pitfall:** if a source value cannot be coerced into the new type (a
non-date string going into a `date` field), that document fails and is
reported under `failures`. Validate or clean such values before reindexing, or
handle them with a script (Part 4).

See [`03_reindex_mapping_change.sh`](./03_reindex_mapping_change.sh)

## Part 4: Reindex with Transformation

A Painless script in the reindex body plus a query to copy only a subset:
rename a field, derive a new field, and drop unwanted documents in flight with
`ctx.op = "noop"`.

See [`04_reindex_transform.sh`](./04_reindex_transform.sh)

## Part 5: Conflicts and Parallelism

`conflicts: "proceed"` skips version conflicts instead of aborting the whole
job; `slices: "auto"` splits the copy into parallel sub-tasks (one per shard)
to use all cores on a large reindex.

See [`05_reindex_conflicts_slices.sh`](./05_reindex_conflicts_slices.sh)

## Part 6: Remote Reindex

Pull data from *another* cluster — the workhorse of a cross-cluster migration
or a major-version upgrade onto a fresh cluster. Note the
`reindex.remote.whitelist` setting required on the destination nodes.

See [`06_remote_reindex.sh`](./06_remote_reindex.sh)

## Part 7: Zero-Downtime Index Migration

The full pattern you reach for in production: applications read and write
through an **alias**, so you can build a corrected index, reindex into it, and
atomically repoint the alias with no downtime for readers.

See [`07_migrate_index.py`](./07_migrate_index.py)

## Part 8: Rolling Upgrade Runbook

Upgrade a cluster one node at a time while it keeps serving traffic:
pre-upgrade health and deprecation checks, snapshot first, disable shard
allocation, replace the binary, restart, re-enable allocation, wait for green,
repeat.

See [`08_rolling_upgrade_runbook.sh`](./08_rolling_upgrade_runbook.sh)

## Cleanup

Remove every index and alias created by this exercise and restore default
shard allocation.

See [`09_cleanup.sh`](./09_cleanup.sh)

## Discussion

- **Field types are immutable** — adding a field is fine, changing one is not.
  Reindex is the supported migration path, which is exactly why production
  applications should target aliases, not concrete index names.
- **Reindex performance** is governed by `slices` (parallelism) and
  `requests_per_second` (throttling so the copy does not starve live traffic).
  Start throttled on a busy cluster and raise it.
- **Always snapshot before an upgrade.** A rolling upgrade is reversible only
  if you can restore. Run the deprecation check (`_migration/deprecations`)
  and clear blockers before you touch the first node.
- **Disable allocation during a node bounce.** Setting
  `cluster.routing.allocation.enable: primaries` stops the cluster from
  frantically rebuilding replicas while a node is briefly down, then re-enable
  it and wait for green before moving to the next node.
- **Remote reindex vs in-place upgrade.** For very old source versions or risky
  upgrades, standing up a new cluster and remote-reindexing into it is often
  safer than upgrading in place.

## Challenge Exercises

1. Reindex with `requests_per_second` set low and watch the throttling in the
   task status, then raise it and compare throughput.
1. Trigger a version conflict deliberately (reindex twice with
   `op_type=create`) and observe the difference between the default and
   `conflicts: "proceed"`.
1. Extend the migrate script to also keep a read alias and a write alias
   separately, swapping each at the right moment.
1. Write a deprecation-check script that fails (non-zero exit) if
   `_migration/deprecations` reports any critical issues.

## Next Steps

1. Pair reindexing with composable templates and aliases
   ([`21_index_templates_aliases`](../21_index_templates_aliases/exercise.md))
1. Snapshot before every upgrade
   ([`19_snapshot_restore`](../19_snapshot_restore/exercise.md))
1. Watch cluster health during the rolling upgrade — see
   [`16_cluster_health_monitoring`](../16_cluster_health_monitoring/)
