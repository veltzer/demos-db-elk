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
- See the [`00_install`](../00_install/exercise.md) exercise if you have not
  set it up yet
- Install required modules:

```bash
pip install elasticsearch
```

## Part 1: Basic Reindex

Copy every document from a source index into a new destination index — no
mapping change, no transformation, just a server-side copy.

See [`01_basic_reindex.sh`](./01_basic_reindex.sh)

## Part 2: Asynchronous Reindex with Task Tracking

For a large index you do not want to hold the HTTP connection open. Passing
`wait_for_completion=false` returns a task id immediately; poll the Tasks API
to watch progress.

See [`02_async_reindex_task.sh`](./02_async_reindex_task.sh)

## Part 3: Reindex to Change a Field Type

The canonical reason `_reindex` exists. You cannot remap a field in place, so
create a new index with the corrected mapping and reindex into it.

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
