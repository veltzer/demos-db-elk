# Monitoring and Alerting for Elasticsearch

## Objective

Turn the raw health APIs into an ongoing monitoring and alerting practice:
build a reusable metrics collector, evaluate metrics against thresholds as a
Nagios-style check, run it from cron, store metrics back into Elasticsearch
for charting in Kibana, and understand the built-in monitoring and Watcher
alerting features.

## Overview

The [`16_cluster_health_monitoring`](../16_cluster_health_monitoring/) exercise
covers the raw health APIs. This exercise is about *operationalising*
them: periodic checks with thresholds, alert routing, a self-monitoring index
so you can chart cluster health over time, and the golden signals a DBA should
actually alert on (without drowning in noise).

The mental model to carry through the exercise is the classic monitoring
pipeline: *collect* raw numbers, *evaluate* them against thresholds, *route*
an alert when something is wrong, and *store* the numbers so you can see
trends. Each part below maps to one of those stages, and the scripts are
layered so later ones reuse earlier ones rather than re-polling the cluster
in their own way.

This exercise covers:

- A reusable Python metrics collector other scripts build on
- A threshold check that exits with Nagios-compatible OK/WARN/CRITICAL codes
- A cron wrapper that stays silent on success and alerts on failure
- Self-monitoring: indexing metrics back into Elasticsearch for Kibana
- A short sampling loop to generate a time series quickly
- Built-in monitoring and Watcher alerting (and the license caveat)
- A reference list of what to alert on, with suggested thresholds

## Prerequisites

- Python 3.x with the `elasticsearch` module
- Elasticsearch running on <http://localhost:9200> with security disabled
- See the [`00_install`](../../shared/00_install/exercise.md) exercise if you
  have not set it up yet
- **Note:** Watcher (script 07) requires a commercial or trial license and is
  not available on the free Basic license. It is included as a reference
- Install required modules:

```bash
pip install elasticsearch
```

## Part 1: The Metrics Collector

A reusable module that polls `_cluster/health`, `_nodes/stats` and
`_cat/indices` and flattens the interesting values (status, heap %, GC,
thread-pool rejections, unassigned shards, store size) into a single dict.
Other scripts import `collect_metrics()`.

**Why a separate collector?** Polling the cluster is the one piece of work
every later script needs. By isolating it in `collect_metrics()`, the
threshold check, the self-monitoring indexer, and the sampling loop all share
exactly the same view of the cluster. There is no risk of one script
measuring heap differently from another, and a fix in one place benefits all
of them. This is just the single-responsibility idea applied to monitoring.

**Why a flat dict?** The collector deliberately returns a flat (non-nested)
dictionary. Each cluster API answers in its own deeply nested JSON shape, but
a flat key/value map is trivial to print, to compare against a threshold, and
to index as one Elasticsearch document where every key becomes a top-level
field. Flattening at collection time means downstream code never has to dig
through nested JSON.

**What's happening under the hood.** Each API answers a different question.
`_cluster/health` is a cheap, cluster-wide summary computed by the elected
master: status colour, shard counts, and pending tasks. `_nodes/stats` is
per-node detail, so the collector loops over every node and keeps the
*worst* value (for example the fullest disk and the highest heap), because a
cluster is only as healthy as its most stressed node. `_cat/indices` lists
the indices so the collector can sum total store size. Reporting the worst
case rather than an average is intentional: an average hides the one node
that is about to hit a disk watermark.

See [`01_metrics_collector.py`](./01_metrics_collector.py)

## Part 2: Threshold Check (Nagios-Style)

Runs the collector, evaluates each metric against a configurable threshold,
prints one OK/WARN/CRITICAL line per check, and exits `0`/`1`/`2` so it can be
wired into any monitoring system.

**Why the exit code matters.** Nagios, Icinga, cron, and most CI systems
judge a command by its exit code, not by parsing its text output. The Nagios
convention is fixed: `0` means OK, `1` means WARNING, `2` means CRITICAL.
By following that convention the same script plugs into a real monitoring
system, a cron job, or a pipeline gate with no glue code. The human-readable
lines are for the on-call engineer; the exit code is for the machine.

**Why report the worst severity.** The script runs several independent
checks but must collapse them into a single exit code. It takes the *maximum*
severity seen: one CRITICAL anywhere makes the whole run CRITICAL. That
mirrors how an operator thinks, since a green heap does not make up for a red
cluster.

**Concept: thresholds encode your service-level objectives.** The
`THRESHOLDS` dict at the top is the only thing you should tune per cluster.
There is no universal "correct" heap or disk percentage; it depends on your
hardware and workload. Some checks (cluster status, unassigned shards,
thread-pool rejections) are categorical rather than numeric, so they are
hard-coded in their own functions instead of living in the dict. A subtle
point in the unassigned-shards check: an unassigned shard on a `red` cluster
is CRITICAL (a missing primary, meaning data is unavailable), but on a
`yellow` cluster it is only a WARNING (usually a missing replica, so data is
still served).

See [`02_threshold_check.py`](./02_threshold_check.py)

## Part 3: Run It From Cron

A wrapper that runs the threshold check, captures the result, and routes an
alert only when the check is not OK — the cron convention of staying silent on
success.

**Why a wrapper at all?** cron already mails any output a job produces to the
crontab owner, but that is a blunt instrument: it cannot reach Slack or a
pager, and it fires even on noise. The wrapper makes routing explicit and
configurable (email and/or a webhook) and, crucially, stays silent when the
check returns OK. Silence on success is what keeps a monitoring system
trustworthy: every message you receive means something is actually wrong.

**What's happening with `set -e`.** The script runs with `set -e`, which
aborts on any non-zero exit. But a WARN or CRITICAL from the check is a
non-zero exit that is *expected and meaningful*, not a bug, so the wrapper
disables `set -e` around the check, captures the exit code, then re-enables
it. It does the same around alert delivery: a missing mail program or an
unreachable webhook is a delivery problem and must not crash the wrapper or
overwrite the real severity it needs to propagate.

**Pitfall: cron has a minimal environment.** A cron job does not inherit
your interactive shell's working directory, `PATH`, or variables. That is why
the wrapper resolves its own directory from `BASH_SOURCE` instead of assuming
a current directory, and why the crontab line uses an absolute path. Settings
like the alert email are read from the environment so you can override them
from the crontab without editing the script.

See [`03_cron_alert_wrapper.sh`](./03_cron_alert_wrapper.sh)

## Part 4: Self-Monitoring Index

The threshold check tells you the state *right now* and then forgets it.
Self-monitoring closes that gap: each run writes its metrics back into
Elasticsearch as a timestamped document, so over time you build a history you
can chart. A pull check answers "is it broken now?"; the stored time series
answers "is it trending toward broken?" and "what did the cluster look like
just before the incident?".

### 4.1 Create the Metrics Index

An index template plus a write alias (`dba-metrics`) so the writer never needs
to know the concrete index name.

**Why an index template?** A template applies field mappings to any index
whose name matches `dba-metrics-*`, before the index exists. Without it,
Elasticsearch would guess types from the first document it sees (dynamic
mapping), and the all-important `@timestamp` could be guessed as text rather
than a `date`, which would make it unusable as a time axis in Kibana. The
template pins `@timestamp` to `date` and the numeric metrics to numeric types
so charts and range queries work correctly from the very first document.

**Why a write alias instead of writing to the index directly?** The writer
targets the alias `dba-metrics`, and the alias points at the concrete index
`dba-metrics-000001`. This indirection means that later, when the index grows
too large, you can roll over to `dba-metrics-000002` and just move the alias;
the writer code never changes because it only ever knows the alias name. This
is the same template-plus-alias pattern that Beats and data streams use under
the hood, which is why the numeric suffix and `is_write_index` flag look the
way they do.

See [`04_create_metrics_index.sh`](./04_create_metrics_index.sh)

### 4.2 Index the Collected Metrics

Stamp the collector output with a UTC `@timestamp` and index one document per
run. Accumulate these and chart them in Kibana (see
[`07_kibana`](../../shared/07_kibana/exercise.md)).

**Why UTC, and why `@timestamp`?** Kibana's time-based views need a date
field to plot against, and the de facto convention across the Elastic Stack
is to name it `@timestamp`. Stamping in UTC avoids the classic bug where
metrics collected in different time zones (or across a daylight-saving change)
appear out of order or shifted on the chart. Kibana converts UTC to the
viewer's local time for display, so storing UTC is always the safe choice.

**What's happening: one document per run.** Each invocation produces a single
self-contained snapshot document. The script uses the bulk helper even for
that one document, on purpose: it is the exact same code path the sampling
loop uses for many documents, so there is one indexing routine to understand
and maintain. It also indexes with `refresh="wait_for"` so the document is
searchable as soon as the call returns, which matters when you immediately
open Kibana to confirm the data arrived.

See [`05_index_metrics.py`](./05_index_metrics.py)

### 4.3 Generate a Quick Time Series

Sample every N seconds for a fixed duration so you can see a line chart
immediately instead of waiting hours for cron to fill in.

**Why a separate loop instead of just cron?** cron's finest granularity is
one minute, and a meaningful trend line needs many points, so building a
chart from cron alone could take hours. The sampling loop is a learning
shortcut: it writes a dozen points in a couple of minutes so you can see a
real line chart now. In production the same `dba-metrics` index is fed by
cron; the loop just front-loads some data.

**Concept: monotonic time for the schedule.** The loop measures elapsed time
with a monotonic clock rather than wall-clock time. A monotonic clock only
ever moves forward and is immune to the system clock being adjusted (by NTP,
for example) mid-run, which keeps the sampling interval honest even if the
machine's calendar time jumps.

See [`06_sample_loop.py`](./06_sample_loop.py)

## Part 5: Built-In Alerting

Everything so far has been *pull-based*: an external scheduler reaches in,
asks the cluster how it is doing, and decides what to do. Elasticsearch also
offers *push-based* alerting that runs inside the cluster itself. The trade-off
is licensing, which the next two sections make concrete.

### 5.1 Watcher (Reference)

A sample Watcher watch that checks cluster health and would notify. Requires a
commercial or trial license, so it is presented as a reference for what
push-based alerting looks like in production.

**Concept: how a watch is structured.** Every Watcher watch is the same four
parts, which is a useful template even outside Elasticsearch: a *trigger*
(when to run, here every minute), an *input* (what data to fetch, here
`_cluster/health`), a *condition* (a test on that data, here status equals
`red`), and *actions* (what to do when the condition is true). The sample uses
a `logging` action so it is harmless to run, but the action slot is exactly
where you would put email, Slack, a webhook, or a pager in production. Because
the watch lives in the cluster and runs on its own schedule, no external cron
is involved.

**Pitfall: the license wall.** On the free Basic license the `PUT` will
return a 403 saying the license is non-compliant for Watcher. That is
expected. You can start a 30-day trial to try it for real (the script shows
the commands), but on Basic the pull-based check from Part 2 is the practical
path.

See [`07_watcher_example.sh`](./07_watcher_example.sh)

### 5.2 Inspect Built-In Monitoring

Read-only inspection of which X-Pack features and licensing are available on
your cluster (self-monitoring, Watcher).

**Why inspect before you build.** Before reaching for Watcher or Stack
Monitoring you need to know what your license actually permits, otherwise you
write alerting that silently never fires. The `_xpack` and `_license`
endpoints answer that question, and the script only reads, so it is safe to
run anywhere. On Basic you will see several features reported as unavailable,
which confirms why this exercise leans on the pull-based approach. The script
also summarizes the production options you graduate to with a license:
Metricbeat shipping to a separate monitoring cluster, and Kibana's built-in
alerting rules.

See [`08_builtin_monitoring_info.sh`](./08_builtin_monitoring_info.sh)

## What to Alert On (Golden Signals)

The hardest part of monitoring is not collecting data but choosing what
deserves to wake someone up. The signals below are the ones that catch the
vast majority of real Elasticsearch incidents. Each maps to an API the
collector already polls, so the table doubles as a guide for extending the
threshold check. Treat the suggested numbers as starting points to tune
against your own cluster's normal baseline, not as fixed truths.

| Signal | Where | Suggested threshold |
| --- | --- | --- |
| Cluster status | `_cluster/health` | alert on `red`; warn on `yellow` |
| Unassigned shards | `_cluster/health` | warn `> 0` (sustained) |
| Heap pressure | `_nodes/stats` jvm | warn `> 75%`, alert `> 85%` |
| GC time | `_nodes/stats` jvm | alert on long/frequent old-gen GC |
| Disk usage | `_cat/allocation` | warn `> 85%`, alert `> 90%` |
| Thread-pool rejections | `_cat/thread_pool` | alert `> 0` (write/search) |
| Pending tasks | `_cluster/health` | alert if growing/not draining |
| Snapshot failures | `_slm/stats` | alert on any failed snapshot |

## Discussion

- **Pull checks vs pushed metrics.** A threshold check (pull) tells you the
  state *right now* and is ideal for cron/Nagios. Indexing metrics back into
  Elasticsearch (push) gives you history and trends in Kibana. You want both.
- **Self-monitoring on the same cluster has a flaw:** if the cluster is down,
  so is your monitoring data. In production, ship metrics to a *separate*
  monitoring cluster (Metricbeat / dedicated monitoring deployment).
- **Golden signals over everything.** Cluster status, unassigned shards, heap,
  disk, thread-pool rejections and snapshot failures catch the vast majority
  of incidents. Start there.
- **Avoid alert fatigue.** Alert on *sustained* breaches, not single samples;
  a brief yellow during a rolling restart is normal. Tune thresholds to your
  cluster's baseline.

## Challenge Exercises

1. Add a per-node disk-percent check to the collector and threshold script.
1. Run the sample loop, then build a Kibana line chart of `heap_percent` over
   time from the `dba-metrics-*` index.
1. Add an SLM snapshot-failure check that reads `_slm/stats`.
1. Start a trial license, install the Watcher watch from script 07, and route a
   real notification (e.g. a webhook action).

## Next Steps

1. Wire the threshold check into your real monitoring system via cron
1. Combine with capacity forecasting
   ([`23_capacity_disk_management`](../23_capacity_disk_management/exercise.md))
1. Snapshot-failure alerting ties into
   ([`19_snapshot_restore`](../19_snapshot_restore/exercise.md))
