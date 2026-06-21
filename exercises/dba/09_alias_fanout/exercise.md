# Hiding Many Indices Behind One Alias

This exercise teaches the operational pattern at the heart of every
time-series and multi-tenant Elasticsearch deployment: keeping data split
across **many small physical indices** while exposing it to the application
as **one stable name**. The application reads from and writes to a single
alias; the DBA quietly adds, rolls, and retires the indices behind it.

## Objective

By the end you will be able to take a fleet of separate indices, place them
behind a single read alias so a query fans out across all of them, designate
one of them as the write target so writes are unambiguous, layer a second
filtered alias over the same data for a scoped view, and run the monthly
maintenance cycle (add the new month, repoint the write index, retire the
oldest month) without the application ever changing a name.

## Overview

A naive Elasticsearch deployment puts all data in one index and lets it grow
forever. That index eventually has shards too large to relocate, queries that
scan years of data to answer a question about today, and a retention policy
that can only be enforced by deleting documents one query at a time.

The fix is to **partition the data into many indices** - one per month, per
day, or per tenant - so each index stays small, queries can skip irrelevant
partitions, and retention becomes a cheap whole-index delete. But partitioning
creates a new problem: the application would now have to know every index name
and keep that list current as indices come and go.

An **alias** solves exactly that. It is a single logical name that resolves to
one *or many* indices:

- A search through the alias **fans out** to every member index and merges the
  results - the application writes one index name and transparently queries
  the whole fleet.
- A write through the alias is routed to the single member flagged as the
  **write index**, so writes are never ambiguous.

The mental model: the alias is the public API, the indices are the private
implementation. You reshape the implementation - add a month, drop a month,
move the write target - entirely behind the alias, and no client is ever the
wiser.

The exercise includes:

- Creating several separate monthly indices (the private implementation)
- Hiding them all behind one read alias and choosing a single write index
- Layering a second, *filtered* alias over the same indices for a scoped view
- The monthly roll: add a new index and atomically repoint the write target
- Retiring the oldest month as a single index delete
- A cleanup script that removes everything

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
set it up yet. This exercise targets Elasticsearch 8.x / 9.x
(`is_write_index` on aliases).

## Files

- `01_create_indices.sh` - Create three separate monthly indices and seed one
  document into each (the private implementation, no alias yet)
- `02_attach_alias.sh` - Hide all three behind one read alias `logs`, mark one
  as the write index, and prove read fan-out and write routing
- `03_filtered_subset_alias.sh` - Add a second alias `logs-errors` over the
  same indices that exposes only `ERROR` documents
- `04_roll_to_new_month.py` - The monthly maintenance job: create the next
  month and atomically move the write index onto it
- `05_retire_old_month.sh` - Retire the oldest month: detach it from the alias
  and delete it in one cheap index drop
- `06_cleanup.sh` - Remove every index and alias the exercise created

## Quick Start

### Step 1: Create the Separate Indices

We start by creating three ordinary, unrelated monthly indices
(`logs-2026.04`, `logs-2026.05`, `logs-2026.06`) and seeding one document into
each. Nothing yet marks them as belonging together - that is deliberate. The
point of the pattern is that the indices are just plain indices; the grouping
lives entirely in the alias we add next. Partitioning by month is the classic
choice because it keeps each index small and makes "expire everything older
than N months" a matter of deleting whole indices rather than scanning for old
documents.

See [`01_create_indices.sh`](./01_create_indices.sh)

### Step 2: Hide Them Behind One Alias

Now the core of the exercise. A single atomic `_aliases` call adds all three
months to one alias named `logs`. After this, a search through `logs` fans out
to every member index and merges the hits - the application names one index
and transparently queries the whole fleet, exactly as if it had typed
`logs-2026.04,logs-2026.05,logs-2026.06` but without ever maintaining that
list.

There is one subtlety that trips everyone up the first time. An alias pointing
at several indices is fine for reads but **ambiguous for writes**: if you POST
a document to `logs`, Elasticsearch cannot guess which of the three indices
should receive it, and it rejects the write. The fix is to flag exactly one
member with `is_write_index: true`. Reads still fan out across all members;
writes all land in that one. This is precisely the mechanism that rollover and
data streams use under the hood - here you operate it by hand so the machinery
is no longer invisible.

The script proves both halves: a `match_all` through the alias returns a
document from each month, while a write through the alias lands only in the
designated write index.

See [`02_attach_alias.sh`](./02_attach_alias.sh)

### Step 3: A Second, Filtered View Over the Same Indices

The same set of indices can sit behind more than one alias, each exposing a
different slice of the data. Here we add a `logs-errors` alias over the same
three months carrying a stored `filter` for `level: ERROR`. That filter is
silently ANDed onto every search through the alias, so `logs-errors` is a
read-only view of just the error lines across all months. It costs nothing in
storage - it is metadata, not a copy - and it lets you hand a team a
pre-scoped name without trusting every client to remember to add the filter.

The script searches both aliases over the identical indices and shows `logs`
returning every level while `logs-errors` returns only the errors.

See [`03_filtered_subset_alias.sh`](./03_filtered_subset_alias.sh)

### Step 4: Roll the Write Index to a New Month

This is the recurring maintenance job. Once a month you create the next
index, add it to the read alias so it becomes searchable, and move
`is_write_index` from the old month to the new one so new documents start
landing there. The application keeps reading and writing the single name
`logs` throughout and never notices the cutover.

The critical detail is that all the alias changes happen in **one**
`_aliases` call. If you split them, there is a window where either two indices
both claim to be the write index (writes become ambiguous and fail) or no
index claims it (writes are rejected). Doing the add-new-write and
demote-old-write together keeps the alias in a valid state at every instant.
Note that the old month is *demoted* (`is_write_index: false`), not removed -
it stays in the alias and remains searchable; it simply stops receiving new
writes.

See [`04_roll_to_new_month.py`](./04_roll_to_new_month.py)

```bash
./04_roll_to_new_month.py
```

### Step 5: Retire the Oldest Month

Retention is the other half of the pattern, and it is where index
partitioning pays off most. Because each month is its own index, expiring
April is a single index delete - no document-by-document deletion, no reindex,
no scanning for old timestamps. We detach April from the alias first so the
read view stays consistent for in-flight queries, then drop the whole index.
The alias quietly shrinks by one member and a fan-out search returns one fewer
month, with no client change.

See [`05_retire_old_month.sh`](./05_retire_old_month.sh)

### Step 6: Clean Up

Aliases vanish automatically when their last backing index is deleted, so
cleanup only has to delete the indices. The script deletes by exact name
rather than a `logs-*` wildcard, so on a shared cluster it never sweeps up
someone else's indices (and Elasticsearch 8+ rejects wildcard deletes by
default anyway).

See [`06_cleanup.sh`](./06_cleanup.sh)

## Discussion

### Read fan-out vs write routing

The two behaviors of a multi-index alias are asymmetric, and keeping them
straight is the whole skill:

- **Reads fan out.** A search, count, or aggregation through the alias runs
  against *every* member index and merges the results. This is free
  indirection - the same as listing all the index names by hand, but without
  the maintenance burden of keeping that list current.
- **Writes route to one.** A multi-index alias has no inherent write target,
  so an indexing request through it is rejected as ambiguous *unless* exactly
  one member is flagged `is_write_index: true`. Exactly one - never zero (no
  target) and never two (ambiguous again).

### Why partition into many indices at all

Splitting one logical data set across many physical indices buys three things
a single giant index cannot:

1. **Bounded shard size.** Each partition stays small, so shards stay in the
   healthy tens-of-GB range and remain quick to relocate and recover.
1. **Cheap retention.** Dropping a partition is a single index delete - by far
   the cheapest way to remove a large block of data. Deleting documents from a
   shared index, by contrast, only tombstones them until a merge reclaims the
   space.
1. **Query pruning.** A query that targets a time range can skip partitions
   that cannot contain matching data, instead of scanning everything.

The alias is what makes all of this invisible to the application.

### Aliases vs data streams vs rollover

This exercise builds the pattern by hand so the moving parts are explicit. In
production you would usually let Elasticsearch automate it:

- A **rollover alias** automates Step 4 - it creates the next backing index
  and moves the write flag for you when a size/age/count condition is met (see
  [`02_index_lifecycle_management`](../02_index_lifecycle_management/exercise.md)).
- A **data stream** hides even the alias and the `is_write_index` flag,
  managing a series of hidden `.ds-...` backing indices automatically. It is
  the modern default for pure append-only time series.

Knowing the manual pattern first means none of that automation is a black box:
a data stream is just this exercise with the bookkeeping done for you.

### One alias, many views

Because an alias is cheap metadata, the same indices can sit behind several
aliases at once - a plain `logs` for everything, a filtered `logs-errors` for
one severity, a per-tenant filtered alias for each customer, a routing alias
to pin a tenant to one shard. None of these duplicate data; each is just a
different lens over the same physical indices. See
[`04_index_templates_aliases`](../04_index_templates_aliases/exercise.md) for
filtered and routing aliases in more depth.

## Challenge

1. Add a per-tenant filtered alias (`logs-tenant-acme`) over the same months
   that only returns documents where `service: acme`, and confirm it spans
   every month.
1. Try to write to the `logs` alias *before* setting `is_write_index` on any
   member (re-run Step 2 but skip the write-index call) and read the exact
   error Elasticsearch returns.
1. In Step 4, deliberately split the atomic roll into two separate
   `_aliases` calls (add-new-write, then demote-old-write) and observe the
   window where two write indices exist - what does a write return then?
1. Replace the hand-rolled monthly roll with a rollover alias plus an ILM
   policy from
   [`02_index_lifecycle_management`](../02_index_lifecycle_management/exercise.md)
   and confirm the write index advances automatically.
1. Partition by tenant instead of by month (`logs-acme`, `logs-globex`, ...),
   hide them all behind one `logs` alias, and give each tenant its own
   filtered alias - the same pattern, a different partition key.

## Next Steps

1. Automate the roll with rollover and ILM
   ([`02_index_lifecycle_management`](../02_index_lifecycle_management/exercise.md)).
1. Combine retention-by-index-delete with snapshots
   ([`03_snapshot_restore`](../03_snapshot_restore/exercise.md)) so a month is
   snapshotted before it is dropped.
1. Explore data streams, which package this entire pattern behind a single
   append-only name.
1. Revisit filtered and routing aliases in depth in
   [`04_index_templates_aliases`](../04_index_templates_aliases/exercise.md).
