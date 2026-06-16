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

## Shared foundations

Both tracks depend on these. Do the install first.

- [`00_install`](./shared/00_install/exercise.md) — install Elasticsearch
  and Kibana (apt, Docker Compose, archive, Podman)
- [`02_bulk`](./shared/02_bulk/exercise.md) — bulk insert and ingest
  performance
- [`04_query_performance`](./shared/04_query_performance/exercise.md) —
  measuring query performance and the impact of field indexing
- [`07_kibana`](./shared/07_kibana/exercise.md) — data visualization and
  analysis in Kibana
- [`09_ssh_tunnel`](./shared/09_ssh_tunnel/exercise.md) — reaching Kibana
  through an SSH tunnel (Linux, macOS, Windows)
- [`12_logstash`](./shared/12_logstash/exercise.md) — Logstash setup and
  data flow
- [`13_streaming_ingestion`](./shared/13_streaming_ingestion/exercise.md) —
  streaming data into an index

## Developer track

Modelling data, querying it, and building search features.

- [`01_crud`](./developer/01_crud/exercise.md) — CRUD operations four ways
  (Kibana, curl, requests, client)
- [`03_dynamic_vs_static_mapping`](./developer/03_dynamic_vs_static_mapping/exercise.md)
  — dynamic vs explicit mappings
- [`05_parent_child`](./developer/05_parent_child/exercise.md) — the
  parent-child (join) relationship model
- [`06_custom_scoring`](./developer/06_custom_scoring/exercise.md) — custom
  relevance with `function_score`
- [`08_nested_vs_object`](./developer/08_nested_vs_object/exercise.md) —
  nested fields vs plain objects
- [`10_parent_child_vs_nested`](./developer/10_parent_child_vs_nested/exercise.md)
  — choosing between nested and parent-child
- [`11_queries_and_aggredations`](./developer/11_queries_and_aggredations/exercise.md)
  — queries and aggregations
- [`14_web_search_application`](./developer/14_web_search_application/exercise.md)
  — a small web search application
- [`15_vector_search`](./developer/15_vector_search/exercise.md) — semantic
  / kNN vector search and hybrid search

## DBA track

Operating and scaling a cluster, and protecting the data lifecycle.

- [`16_cluster_health_monitoring`](./dba/16_cluster_health_monitoring/exercise.md)
  — cluster and node health, allocation explain, hot threads
- [`17_shard_management`](./dba/17_shard_management/exercise.md) — shard
  sizing, replicas, shrink / split / forcemerge
- [`18_index_lifecycle_management`](./dba/18_index_lifecycle_management/exercise.md)
  — ILM policies, rollover, data streams, retention
- [`19_snapshot_restore`](./dba/19_snapshot_restore/exercise.md) — backup,
  restore, SLM, and a disaster-recovery drill
- [`21_index_templates_aliases`](./dba/21_index_templates_aliases/exercise.md)
  — composable templates and zero-downtime alias swaps
- [`22_performance_tuning`](./dba/22_performance_tuning/exercise.md) — heap,
  caches, thread pools, circuit breakers, slow logs
- [`23_capacity_disk_management`](./dba/23_capacity_disk_management/exercise.md)
  — disk watermarks, the flood-stage incident, capacity forecasting
- [`24_reindex_upgrade`](./dba/24_reindex_upgrade/exercise.md) — reindexing
  and the rolling upgrade runbook
- [`25_monitoring_alerting`](./dba/25_monitoring_alerting/exercise.md) —
  metrics collection, threshold checks, and alerting

## Notes on numbering

Folder number prefixes are kept from the original flat layout, so they are
not contiguous within a track (for example the DBA track starts at `16`).
The numbers preserve a stable ordering and keep each exercise's internal
links intact; they are not meant to be read as "do 1 through N in order"
across tracks.
