# Elasticsearch / ELK Exercises

These hands-on exercises are organised into three tracks by audience:

- **Shared foundations** — install and core operational skills both
  developers and DBAs need.
- **Developer track** — data modelling, querying, search relevance and
  building search-backed applications.
- **DBA track** — operating, scaling, securing the data lifecycle, and
  keeping an Elasticsearch cluster healthy and recoverable.

Each exercise lives in its own folder with an `exercise.md` (the
instructions) and numbered runnable `.sh` / `.py` scripts. Start with the
shared foundations, then follow whichever track matches your role.

## Resetting between exercises

Each exercise creates indices, templates, policies and other objects. To keep
runs independent, reset the cluster to its post-install state **before and
after every exercise**. Two scripts in [`../scripts`](../scripts) handle this:

- [`elk_capture_baseline.py`](../scripts/elk_capture_baseline.py) — run this
  **once**, on a freshly installed cluster (right after
  [`00_install`](./shared/00_install/exercise.md), before doing any exercise).
  It records the names of everything Elasticsearch and Kibana ship with, plus
  the cluster settings, to `~/elk_baseline.json`. This file is your machine's
  definition of "default", so it is not committed to the repo.
- [`elk_reset.py`](../scripts/elk_reset.py) — run this before and after each
  exercise. It deletes everything present now but **not** in the baseline
  (your indices, templates, ILM/SLM policies, ingest pipelines, snapshot
  repositories, transforms and data streams) and resets all cluster settings
  to their defaults, returning the cluster to the captured baseline.

```bash
# once, on a fresh install:
./scripts/elk_capture_baseline.py

# before and after each exercise:
./scripts/elk_reset.py        # quiet; add -v to see what was removed
```

The reset is **idempotent** (running it twice is the same as once) and quiet
by default. Both scripts honour `ES_URL` (default `http://localhost:9200`) and
`ELK_BASELINE` (default `~/elk_baseline.json`). The reset refuses to touch a
non-local cluster unless you set `ELK_RESET_ALLOW_REMOTE=1`, because it is
destructive.

Two limits worth knowing: the reset deletes objects by **name**, so it does
not restore the internal contents of a built-in object that an exercise edited
in place; and it cannot revert node-level configuration
(`elasticsearch.yml`, JVM heap size, `node.attr.*`), which lives on disk rather
than in the REST API and needs a container or process restart. These affect
only a couple of DBA exercises (`05_performance_tuning`, parts of
`06_capacity_disk_management`).

## Shared foundations

Both tracks depend on these. Do the install first.

- [`00_install`](./shared/00_install/exercise.md) — install Elasticsearch
  and Kibana (apt, Docker Compose, archive, Podman)
- [`01_bulk`](./shared/01_bulk/exercise.md) — bulk insert and ingest
  performance
- [`02_query_performance`](./shared/02_query_performance/exercise.md) —
  measuring query performance and the impact of field indexing
- [`03_ssh_tunnel`](./shared/03_ssh_tunnel/exercise.md) — reaching Kibana
  through an SSH tunnel (Linux, macOS, Windows)
- [`04_kibana`](./shared/04_kibana/exercise.md) — data visualization and
  analysis in Kibana
- [`05_logstash`](./shared/05_logstash/exercise.md) — Logstash setup and
  data flow
- [`06_streaming_ingestion`](./shared/06_streaming_ingestion/exercise.md) —
  streaming data into an index

## Developer track

Modelling data, querying it, and building search features.

- [`00_crud`](./developer/00_crud/exercise.md) — CRUD operations four ways
  (Kibana, curl, requests, client)
- [`01_dynamic_vs_static_mapping`](./developer/01_dynamic_vs_static_mapping/exercise.md)
  — dynamic vs explicit mappings
- [`02_parent_child`](./developer/02_parent_child/exercise.md) — the
  parent-child (join) relationship model
- [`03_custom_scoring`](./developer/03_custom_scoring/exercise.md) — custom
  relevance with `function_score`
- [`04_nested_vs_object`](./developer/04_nested_vs_object/exercise.md) —
  nested fields vs plain objects
- [`05_parent_child_vs_nested`](./developer/05_parent_child_vs_nested/exercise.md)
  — choosing between nested and parent-child
- [`06_queries_and_aggregations`](./developer/06_queries_and_aggregations/exercise.md)
  — queries and aggregations
- [`07_web_search_application`](./developer/07_web_search_application/exercise.md)
  — a small web search application
- [`08_vector_search`](./developer/08_vector_search/exercise.md) — semantic
  / kNN vector search and hybrid search

## DBA track

Operating and scaling a cluster, and protecting the data lifecycle.

- [`00_cluster_health_monitoring`](./dba/00_cluster_health_monitoring/exercise.md)
  — cluster and node health, allocation explain, hot threads
- [`01_shard_management`](./dba/01_shard_management/exercise.md) — shard
  sizing, replicas, shrink / split / forcemerge
- [`02_index_lifecycle_management`](./dba/02_index_lifecycle_management/exercise.md)
  — ILM policies, rollover, data streams, retention
- [`03_snapshot_restore`](./dba/03_snapshot_restore/exercise.md) — backup,
  restore, SLM, and a disaster-recovery drill
- [`04_index_templates_aliases`](./dba/04_index_templates_aliases/exercise.md)
  — composable templates and zero-downtime alias swaps
- [`05_performance_tuning`](./dba/05_performance_tuning/exercise.md) — heap,
  caches, thread pools, circuit breakers, slow logs
- [`06_capacity_disk_management`](./dba/06_capacity_disk_management/exercise.md)
  — disk watermarks, the flood-stage incident, capacity forecasting
- [`07_reindex_upgrade`](./dba/07_reindex_upgrade/exercise.md) — reindexing
  and the rolling upgrade runbook
- [`08_monitoring_alerting`](./dba/08_monitoring_alerting/exercise.md) —
  metrics collection, threshold checks, and alerting
- [`09_alias_fanout`](./dba/09_alias_fanout/exercise.md) — hiding many
  indices behind one alias: read fan-out, a single write index, and the
  monthly roll
