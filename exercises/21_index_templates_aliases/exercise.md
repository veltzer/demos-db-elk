# Index Templates and Aliases in Elasticsearch

## Objective

Learn how a DBA standardizes index configuration with composable templates
and performs zero-downtime operational changes with aliases. By the end you
will be able to build reusable component templates, compose them into
priority-ordered index templates, simulate them before applying, and use
aliases (plain, filtered, and routing) to swap a new index mapping into
production without any downtime.

## Overview

This exercise covers, with runnable scripts:

1. **Component templates** - reusable bundles of settings and mappings.
1. **Composable index templates** - tie components together with
   `index_patterns`, `composed_of`, `priority`, and inline overrides.
1. **Simulation** - preview the resolved configuration before creating any
   index.
1. **Verification** - create an index from a pattern and confirm it
   inherited the template configuration.
1. **Alias basics** - atomic add/remove and querying through an alias.
1. **Filtered and routing aliases** - expose a subset of an index or pin to
   shards.
1. **Zero-downtime reindex** - swap a new mapping into production via an
   atomic alias repoint.
1. **Cleanup**.

All examples use the modern composable template API
(`_component_template` and `_index_template`), not the deprecated legacy
`_template` API.

## Prerequisites

- Python 3.x with the `elasticsearch` module:

```bash
pip install elasticsearch
```

- Elasticsearch running on <http://localhost:9200> with security disabled
  (plain HTTP). If it is not installed yet, see
  [`../00_install`](../00_install).

## Part 1: Component Templates

A component template is a named, standalone bundle of settings and/or
mappings. On its own it does nothing; it only takes effect when an index
template references it. This lets you define a piece once and reuse it
across many templates.

We create two: a `common-settings` component (shards, replicas, refresh
interval) and a `logs-mappings` component (the field types shared by every
log index).

See [`01_component_templates.sh`](./01_component_templates.sh)

## Part 2: Composable Index Templates and Precedence

A composable index template applies to any new index whose name matches one
of its `index_patterns`. It merges the listed `composed_of` components, then
applies the inline `template` block (which has the highest precedence), and
declares a `priority`.

We create two templates to demonstrate precedence: `logs-template`
(pattern `logs-*`, priority 100) and `logs-audit-template` (pattern
`logs-audit-*`, priority 200). When an index name matches both patterns,
only the higher-priority template applies.

See [`02_composable_template.sh`](./02_composable_template.sh)

## Part 3: Simulate Before Applying

Before creating any index, you can ask Elasticsearch exactly what
configuration a name would resolve to. `_simulate_index/<name>` shows which
templates match a concrete name and the merged result, while `_simulate`
with a body lets you trial an unsaved template.

See [`03_simulate_template.sh`](./03_simulate_template.sh)

## Part 4: Create an Index and Verify Inheritance

Now create real indices and confirm the settings and mappings came from the
templates - we never specify them on the create call. `logs-app-2024`
inherits from `logs-template`; `logs-audit-2024` inherits from the
higher-priority `logs-audit-template`.

See [`04_create_and_verify.sh`](./04_create_and_verify.sh)

## Part 5: Alias Basics

An alias is a second name pointing at one or more indices. Clients talk to
the alias, so the DBA can repoint it later without touching client config.
The `_aliases` API applies a list of actions atomically.

See [`05_aliases_basics.sh`](./05_aliases_basics.sh)

## Part 6: Filtered and Routing Aliases

An alias can carry a `filter` so it only exposes a subset of an index, and a
`routing` value so reads and writes through it are pinned to specific
shards. These give lightweight per-tenant or per-severity views without
copying data.

See [`06_filtered_routing_aliases.sh`](./06_filtered_routing_aliases.sh)

## Part 7: Zero-Downtime Mapping Change via Alias Swap

You cannot change the type of an existing field in place. To change a
mapping you must build a new index and move the data across. The classic
pattern uses two aliases - `app-write` and `app-read` - so clients never
talk to a concrete index. You create v2 with the new mapping, `_reindex`
v1 into v2 while v1 keeps serving reads, then atomically repoint both
aliases from v1 to v2 in a single `_aliases` call. Because remove and add
happen in one transaction, there is never a window where the alias points
at zero indices.

This Python script performs the whole swap and verifies counts before and
after to prove no documents were lost.

See [`07_zero_downtime_swap.py`](./07_zero_downtime_swap.py)

## Part 8: Cleanup

Remove the indices, index templates, and component templates created above.
Note the deletion order: index templates must go before the component
templates they reference, because a component template that is in use
cannot be deleted.

See [`08_cleanup.sh`](./08_cleanup.sh)

## Discussion

### Why aliases enable zero-downtime mapping changes

Field types are immutable: once `status_code` is a `keyword`, it stays a
`keyword` for the life of that index. The only way to "change" it is to
create a fresh index with the desired mapping and reindex the data. If
clients referenced the concrete index name, you would have to delete and
recreate it (a downtime window) or coordinate a config change across every
client. By having clients reference an alias instead, the DBA owns the
indirection: build the new index out of band, reindex into it, then flip the
alias. The flip is a single atomic `_aliases` call that performs the
`remove` of the old index and the `add` of the new one together, so reads
never see a missing index.

### Template precedence

When several composable index templates match the same new index name, only
ONE applies: the one with the highest `priority`. There is no merging across
competing index templates. Within the chosen template, the layers are merged
in order: the `composed_of` components first (later components win on
conflicts), and finally the inline `template` block, which always wins. Use
`_simulate_index` whenever you are unsure which template a name will pick.

### Component reuse

Component templates let you express policy once - a standard shard/replica
layout, a shared set of log fields, an ILM policy reference - and reference
it from many index templates. Changing the component updates the resolved
configuration for every future index that composes it, without editing each
template. This keeps a large index estate consistent and dry.

### Filtered and routing aliases

A filtered alias attaches a query that is ANDed onto every search through
the alias, producing a read-only view of a subset (for example only
`ERROR` documents, or only one tenant's rows). A routing alias pins the
shard routing for reads and writes through it, so a tenant's documents
co-locate on one shard and searches can target just that shard. Both are
metadata-only - no data is duplicated - which makes them cheap to create
and change.

## Challenge Exercises

1. Add a third component template (for example an ILM policy reference) and
   compose it into `logs-template`, then re-simulate to see the merged
   result.
1. Create an index named `logs-audit-payments-2024` and predict, before
   running `_simulate_index`, which template wins and why.
1. Extend the swap script to keep both v1 and v2 attached to `app-read`
   during reindex, then narrow it to v2 only - observe the count while both
   are attached.
1. Build a filtered alias per service (`checkout`, `api`) and confirm each
   only returns its own documents.
1. Add a `is_write_index` flag to one member of a multi-index alias and read
   the docs on rollover-style write aliases.

## Next Steps

1. Combine these templates with the Index Lifecycle Management exercise
   (`../18_index_lifecycle_management`) to auto-rollover time-series
   indices.
1. Use a write alias plus the rollover API for hands-off index size
   management.
1. Script the alias swap into a repeatable migration tool with rollback.
1. Explore data streams, which build on composable templates and a hidden
   write alias for append-only time-series data.
