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
- See the [`00_install`](../00_install/exercise.md) exercise if you have not
  set it up yet
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

See [`01_metrics_collector.py`](./01_metrics_collector.py)

## Part 2: Threshold Check (Nagios-Style)

Runs the collector, evaluates each metric against a configurable threshold,
prints one OK/WARN/CRITICAL line per check, and exits `0`/`1`/`2` so it can be
wired into any monitoring system.

See [`02_threshold_check.py`](./02_threshold_check.py)

## Part 3: Run It From Cron

A wrapper that runs the threshold check, captures the result, and routes an
alert only when the check is not OK — the cron convention of staying silent on
success.

See [`03_cron_alert_wrapper.sh`](./03_cron_alert_wrapper.sh)

## Part 4: Self-Monitoring Index

### 4.1 Create the Metrics Index

An index template plus a write alias (`dba-metrics`) so the writer never needs
to know the concrete index name.

See [`04_create_metrics_index.sh`](./04_create_metrics_index.sh)

### 4.2 Index the Collected Metrics

Stamp the collector output with a UTC `@timestamp` and index one document per
run. Accumulate these and chart them in Kibana (see
[`07_kibana`](../07_kibana/exercise.md)).

See [`05_index_metrics.py`](./05_index_metrics.py)

### 4.3 Generate a Quick Time Series

Sample every N seconds for a fixed duration so you can see a line chart
immediately instead of waiting hours for cron to fill in.

See [`06_sample_loop.py`](./06_sample_loop.py)

## Part 5: Built-In Alerting

### 5.1 Watcher (Reference)

A sample Watcher watch that checks cluster health and would notify. Requires a
commercial or trial license, so it is presented as a reference for what
push-based alerting looks like in production.

See [`07_watcher_example.sh`](./07_watcher_example.sh)

### 5.2 Inspect Built-In Monitoring

Read-only inspection of which X-Pack features and licensing are available on
your cluster (self-monitoring, Watcher).

See [`08_builtin_monitoring_info.sh`](./08_builtin_monitoring_info.sh)

## What to Alert On (Golden Signals)

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
