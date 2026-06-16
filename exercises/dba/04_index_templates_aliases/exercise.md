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

Why this matters: in production you rarely create indices by hand and spell
out their settings and mappings each time. New indices appear automatically
(a daily log index, a rollover, a data stream segment) and each one must be
configured correctly the moment it is born. Templates are how Elasticsearch
applies that configuration the instant a matching index is created. Aliases
are the complementary tool: they let you change which physical index a name
resolves to without touching any client. Together they are the backbone of
how a DBA operates a cluster without scheduled downtime.

## Prerequisites

- Python 3.x with the `elasticsearch` module:

```bash
pip install elasticsearch
```

- Elasticsearch running on <http://localhost:9200> with security disabled
  (plain HTTP). If it is not installed yet, see
  [`../00_install`](../../shared/00_install).

## Part 1: Component Templates

A component template is a named, standalone bundle of settings and/or
mappings. On its own it does nothing; it only takes effect when an index
template references it. This lets you define a piece once and reuse it
across many templates.

We create two: a `common-settings` component (shards, replicas, refresh
interval) and a `logs-fields` component (the field types shared by every
log index). We avoid the name `logs-mappings` on purpose: a stack-managed
component template of that exact name ships with x-pack/Kibana and the stack
restores it periodically, so an exercise component of that name would be
silently clobbered.

The split into a settings component and a fields component is deliberate.
Settings (shard count, replicas, refresh interval) tend to be the same
across many unrelated index families, while mappings differ by data type.
Keeping them in separate components means you can mix and match: a metrics
template might reuse `common-settings` but pair it with a `metrics-fields`
component instead. This is the same single-responsibility idea you apply
when factoring code into small reusable functions.

The `_meta` block carries no behavior; it is free-form metadata for humans.
Recording an owner and a description there is good operational hygiene,
because months later someone needs to know who created a template and why
before they dare to change it.

A common pitfall worth internalizing now: a component template is inert.
If you create one and then query a new index, nothing happens, because no
index template references it yet. Components only contribute configuration
when pulled in through an index template's `composed_of` list in Part 2.

See [`01_component_templates.sh`](./01_component_templates.sh)

## Part 2: Composable Index Templates and Precedence

A composable index template applies to any new index whose name matches one
of its `index_patterns`. It merges the listed `composed_of` components, then
applies the inline `template` block (which has the highest precedence), and
declares a `priority`.

What is happening under the hood: when you create an index, Elasticsearch
does not consult your create request alone. It scans every registered index
template, finds the ones whose patterns match the new name, picks the single
winner by priority, then builds the final configuration by layering the
matched components and the inline `template` block in order. Only after that
resolution does the index come into existence. The inline `template` block
sits on top of the components precisely so a template can override or extend
what a shared component provides without forking the component itself. Here
`logs-template` reuses the shared field component but bumps replicas to 1
and adds a `host` field on top.

We create two templates to demonstrate precedence: `logs-template`
(pattern `logs-*`, priority 150) and `logs-audit-template` (pattern
`logs-audit-*`, priority 200). When an index name matches both patterns,
only the higher-priority template applies.

> Note on priority 150: a stack-managed template named `logs` (pattern
> `logs-*-*`, priority 100) ships with x-pack/Kibana. Elasticsearch refuses to
> register two templates whose patterns can overlap at the same priority, so
> `logs-*` at priority 100 would be rejected on such a cluster. Using 150 keeps
> `logs-template` below the audit template (200) while avoiding that clash.

The priority rule and the "patterns may not overlap at the same priority"
rule together remove ambiguity by design. Elasticsearch never has to guess
which template wins, and it never silently merges two competing templates.
This is a deliberate contrast with the deprecated legacy `_template` API,
where overlapping templates were merged and the result was hard to predict.
The lesson: priority is not a hint, it is the tie-breaker, and the cluster
enforces that the tie-breaker is always decisive.

See [`02_composable_template.sh`](./02_composable_template.sh)

## Part 3: Simulate Before Applying

Before creating any index, you can ask Elasticsearch exactly what
configuration a name would resolve to. `_simulate_index/<name>` shows which
templates match a concrete name and the merged result, while `_simulate`
with a body lets you trial an unsaved template.

Why this matters: template resolution is invisible until an index is born,
and by then the mapping is committed and largely immutable. Simulation moves
that resolution earlier, so you see the final settings and mappings before
anything is created. The output also reports the `overlapping` templates,
which are the ones that matched the name by pattern but lost on priority.
That field is your proof that precedence resolved the way you expected,
which is exactly the kind of thing that is easy to get wrong by eye.

The script simulates `logs-audit-2024` (both templates match, the audit
template wins, so you should see replicas 2 plus the `actor` and `action`
fields) and `logs-2024` (only `logs-template` matches, so replicas 1 and a
`host` field, but no audit fields). The third call simulates an unsaved
template body at priority 160 rather than 150. The same overlap rule from
Part 2 applies during simulation: a `logs-*` candidate at priority 150 would
clash with the already-saved template, so the example uses 160 to make it a
distinct, resolvable candidate.

See [`03_simulate_template.sh`](./03_simulate_template.sh)

## Part 4: Create an Index and Verify Inheritance

Now create real indices and confirm the settings and mappings came from the
templates - we never specify them on the create call. `logs-app-2024`
inherits from `logs-template`; `logs-audit-2024` inherits from the
higher-priority `logs-audit-template`.

This step closes the loop: simulation predicted the configuration, and now
the live index proves the prediction. The key insight is that the create
calls are deliberately bare. Because the names match the patterns, the
templates do all the work, which is precisely how automatic index creation
behaves in production. If the verified mapping matches what the simulation
showed, you can trust the template to configure every future index that
matches the pattern, not just these two.

See [`04_create_and_verify.sh`](./04_create_and_verify.sh)

## Part 5: Alias Basics

An alias is a second name pointing at one or more indices. Clients talk to
the alias, so the DBA can repoint it later without touching client config.
The `_aliases` API applies a list of actions atomically.

Think of an alias as a layer of indirection, the same idea as a symbolic
link in a filesystem or a stable hostname in front of changing servers.
A query against an alias is resolved to its backing index or indices and
runs exactly as if you had named the index directly, so clients need no
special handling. The atomicity of `_aliases` is the load-bearing detail:
the API takes a list of `add` and `remove` actions and applies them as one
all-or-nothing transaction. That guarantee is what lets you remove the old
index and add the new one in the same instant, with no window in between
where the alias points at nothing. The script demonstrates this by
repointing `logs-current` from one index to another and back, both as
single atomic calls.

See [`05_aliases_basics.sh`](./05_aliases_basics.sh)

## Part 6: Filtered and Routing Aliases

An alias can carry a `filter` so it only exposes a subset of an index, and a
`routing` value so reads and writes through it are pinned to specific
shards. These give lightweight per-tenant or per-severity views without
copying data.

A filtered alias works by silently combining its stored query with every
search that goes through it, so a search through `logs-errors` can never
return an `INFO` document even though those documents sit in the same
physical index. This is a view, not a copy: it costs nothing in storage and
changing the filter is a metadata update, not a reindex. It is also not a
security boundary on its own, just a convenient scoping tool.

A routing alias pins the shard-routing value for reads and writes. Normally
Elasticsearch hashes a document's id to choose a shard; supplying a routing
value forces all documents sharing that value onto the same shard. The
payoff is that a search for one tenant can target a single shard instead of
fanning out to all of them. With the one-shard index in this exercise the
effect is invisible, but the configuration is identical at any shard count,
which is the point of practicing it here.

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

The reason a new index is unavoidable is that a field's type is fixed at
creation. The script starts v1 with `status_code` mapped as a `keyword`,
which means range queries and numeric aggregations cannot work on it, then
fixes it to `integer` in v2. You cannot edit that type in place; the only
way forward is a fresh index plus `_reindex`, which re-reads every source
document and writes it through the new mapping. Splitting the alias into a
read name and a write name lets reads keep flowing from v1 throughout the
copy, since only after the copy completes does the single atomic swap move
both names to v2. The script then asserts that the before and after counts
match and runs the previously impossible range query to prove the new
mapping is live. The numbered v1 and v2 names (`app-000001`, `app-000002`)
mirror the convention the rollover API uses, which is why this same pattern
generalizes to automated index management.

See [`07_zero_downtime_swap.py`](./07_zero_downtime_swap.py)

## Part 8: Cleanup

Remove the indices, index templates, and component templates created above.
Note the deletion order: index templates must go before the component
templates they reference, because a component template that is in use
cannot be deleted.

This ordering is a small lesson in dependency management. The reference goes
from index template to component, so teardown runs in the opposite direction
to setup. Elasticsearch enforces it: it refuses to delete a component while
any index template still composes it, exactly as a database refuses to drop
a table another table still references. Deleting templates does not touch
indices that were already created from them, since a template only shapes an
index at birth and has no further hold over it afterward.

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
