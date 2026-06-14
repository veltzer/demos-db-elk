# Elasticsearch Snapshot and Restore Exercise

This exercise teaches the backup and disaster-recovery workflow every
Elasticsearch DBA must own: registering a snapshot repository, taking
incremental snapshots, restoring data, automating it all with Snapshot
Lifecycle Management (SLM), and proving your backups actually work with a
disaster-recovery drill.

## Overview

Snapshots are the official, supported way to back up Elasticsearch. A
snapshot is a point-in-time, incremental copy of one or more indices (and
optionally the cluster state) written into a *repository*. Restores read
that data back into a cluster. This exercise walks the full lifecycle:

- Set the `path.repo` prerequisite and register a filesystem repository
- Create sample indices with data to protect
- Take full and selective snapshots and watch their status
- List and inspect existing snapshots
- Restore data: full restore, and a safe restore under a new name
- Run an automated DR drill that backs up, destroys, restores and verifies
- Automate everything with an SLM policy plus retention
- Clean up snapshots, the policy and the repository

## Objective

By the end you will be able to design a working backup-and-recovery
strategy for an Elasticsearch cluster, automate it, and verify it.

## Prerequisites

### 1. Python and the Elasticsearch client

Use Python 3.x with the official client installed:

```bash
pip install elasticsearch
```

### 2. Elasticsearch running with security disabled

Elasticsearch must be reachable on <http://localhost:9200> over plain HTTP
with security disabled. See the
[`00_install`](../../shared/00_install/exercise.md) exercise if you have not
set it up yet.

### 3. important: configure `path.repo` and restart

A filesystem (`fs`) repository can only write to directories that are
explicitly allow-listed in the `path.repo` node setting. If you skip this,
registering the repository fails with:

```text
[location] location [...] doesn't match any of the locations
specified by path.repo
```

`path.repo` is a **static** setting: you must set it in configuration and
**restart** Elasticsearch. It cannot be changed at runtime through the API.
On a multi-node cluster the location must be a **shared filesystem mounted
at the same path on every node** (NFS, etc.); a plain local directory only
works for a single-node cluster.

#### Native install (archive / apt / rpm)

Edit `elasticsearch.yml` (usually `/etc/elasticsearch/elasticsearch.yml`
for the apt/rpm package, or `config/elasticsearch.yml` for the archive)
and add:

```yaml
path.repo: ["/tmp/es_snapshots"]
```

Create the directory and make it writable by the Elasticsearch user, then
restart the service:

```bash
sudo mkdir -p /tmp/es_snapshots
sudo chown elasticsearch:elasticsearch /tmp/es_snapshots
sudo systemctl restart elasticsearch
```

#### docker-compose

The container already exposes `/usr/share/elasticsearch/snapshots` as the
conventional repo path. You must do two things: pass `path.repo` as an
environment variable, and mount a volume there so the data survives a
container restart. Add to your service:

```yaml
services:
  elasticsearch:
    environment:
      - path.repo=/usr/share/elasticsearch/snapshots
    volumes:
      - es_snapshots:/usr/share/elasticsearch/snapshots

volumes:
  es_snapshots:
```

Then recreate the container: `docker compose up -d`.

In the scripts below the repository `location` is `"backups"`, which is
interpreted **relative to the first `path.repo` entry**. So with
`path.repo: ["/tmp/es_snapshots"]` the snapshots land in
`/tmp/es_snapshots/backups`.

## Files

- `01_register_repository.sh` - Register and verify the `fs` repository
- `02_create_sample_data.sh` - Create the `customers` and `orders` indices
- `03_take_snapshot.sh` - Take a full and a selective snapshot, show status
- `04_list_snapshots.sh` - List and inspect snapshots (`_all`, `_cat`)
- `05_restore_snapshot.sh` - Full restore plus a rename restore
- `06_dr_drill.py` - Automated DR drill printing PASS / FAIL
- `07_slm_policy.sh` - Create, run and inspect an SLM policy with retention
- `08_cleanup.sh` - Delete snapshots, the policy and the repository

## Step-by-step

### Step 1: Register the repository

After `path.repo` is configured and Elasticsearch is restarted, register
the filesystem repository and verify every node can reach it.

A repository is just named configuration: it tells Elasticsearch *where*
and *how* to store snapshot blobs. Registering it with `PUT
_snapshot/<repo>` does not copy any data yet; it only records the type
(`fs`) and settings (the `location`, and `compress` which gzip-compresses
the small metadata files, not the already-compressed Lucene segments).
The final `_verify` call is the important habit: it asks every node to
write and read a test blob in the location, which catches the classic
mistake of a shared filesystem mounted on only some nodes before that
mistake silently breaks a real snapshot.

See [`01_register_repository.sh`](./01_register_repository.sh)

### Step 2: Create sample data

Create two small indices so we have something worth backing up, and so
later steps can show selective snapshots and restores.

Both indices are created with a single shard and zero replicas to keep
the demo fast and deterministic on a single node. The mappings are
explicit so the snapshot captures real field definitions, not just
documents: a snapshot stores each index's settings and mappings
alongside its data, so a restore rebuilds the index exactly as it was.
Having two separate indices (`customers` and `orders`) is what lets
later steps demonstrate backing up or restoring one index without
touching the other.

See [`02_create_sample_data.sh`](./02_create_sample_data.sh)

### Step 3: Take snapshots

Take a full snapshot of all indices and a selective snapshot of just
`customers`, then inspect the detailed per-shard status.

The full snapshot uses `include_global_state: true` so it also captures
cluster-level configuration (templates, persistent settings, ILM
policies, ingest pipelines), while the selective one sets it to `false`
to stay focused on a single index. The `wait_for_completion=true`
parameter makes the API block until the snapshot finishes; in real
automation you usually leave it off so the call returns immediately and
you poll `_status` instead. The custom `metadata` block (who took it and
why) is free-form annotation that travels with the snapshot, which helps
when you are staring at a list of backups months later. The `_status`
call breaks the work down per shard and reports `STARTED` while copying
and `SUCCESS` once done.

See [`03_take_snapshot.sh`](./03_take_snapshot.sh)

### Step 4: List and inspect snapshots

See what backups exist, in full JSON and as a compact `_cat` table.

The `_all` form returns rich JSON (state, start and end times, the list
of indices, any failures) and is what monitoring tools parse, while the
`_cat/snapshots` table is the human-friendly view for a quick glance.
Knowing what is in the repository before a crisis is half the battle:
under pressure you want to pick the right snapshot quickly, not discover
its contents during the restore.

See [`04_list_snapshots.sh`](./04_list_snapshots.sh)

### Step 5: Restore

Simulate losing the `orders` index and restore it, then restore
`customers` under the new name `restored_customers` using
`rename_pattern` / `rename_replacement` so production is never touched.

The key rule is that you cannot restore over an open index of the same
name; Elasticsearch refuses rather than risk corrupting live data. So
the first restore deletes `orders` first (simulating real data loss),
then restores it cleanly. The second restore shows the safer pattern:
`rename_pattern` is a regular expression matched against each restored
index name, and its capture groups are substituted into
`rename_replacement`. Here `(.+)` captures the whole name and
`restored_$1` turns `customers` into `restored_customers`, so the live
index is never overwritten. This rename trick is how you inspect a
backup, or recover a single corrupted document, without disturbing
production. The restore also overrides `number_of_replicas` to show that
you can change index settings at restore time, which is handy when
recovering into a smaller cluster.

See [`05_restore_snapshot.sh`](./05_restore_snapshot.sh)

### Step 6: Run a disaster-recovery drill

This is the most important step. A backup you have never restored is not a
backup. This script loads known data, snapshots it, deletes the index,
restores it, and compares document counts, printing PASS or FAIL. It is
genuinely runnable end to end once `path.repo` is configured.

The drill works against a throwaway index with a *known* document count,
so the verification is unambiguous: if the restored count does not match
exactly, something is wrong and it fails loudly. One subtlety worth
noting is that the restore call returns as soon as shards begin
recovering, not when they are searchable, so the script waits for
cluster health to reach `yellow` and then refreshes before counting.
Skipping that wait is a common cause of a "passing" backup that actually
counted zero documents. The script also times the whole loop, which is
exactly how you measure a real RTO. Because every step is idempotent
(it deletes leftovers from prior runs), you can safely run it on a
schedule.

See [`06_dr_drill.py`](./06_dr_drill.py)

```bash
./06_dr_drill.py
```

### Step 7: Automate with SLM

Create a Snapshot Lifecycle Management policy that snapshots on a schedule
and prunes old snapshots automatically, run it once on demand, and inspect
the policy state and cluster-wide SLM stats.

The policy bundles a cron schedule (`0 30 1 * * ?` is 01:30 daily), a
name template using date math (`<daily-snap-{now/d}>` so each run gets a
unique timestamped name and they never collide), the target repository,
the snapshot config, and a retention rule. The `_execute` call fires the
policy immediately rather than waiting for the schedule, which is how you
smoke-test a new policy without waiting a day. Reading the policy back
shows `last_success`, `last_failure`, and the next scheduled run, and
`_slm/stats` aggregates taken, failed, and deleted counts across all
policies; together they are what you alert on so a silently failing
backup job cannot go unnoticed.

See [`07_slm_policy.sh`](./07_slm_policy.sh)

### Step 8: Clean up

Delete the snapshots, the SLM policy, the repository registration and the
sample indices.

Note the distinction between unregistering a repository and deleting its
data. Deleting the snapshots (`DELETE _snapshot/<repo>/<snap>`) actually
frees blobs in the repository, while removing the repository
registration only detaches Elasticsearch from the location and leaves any
remaining files on disk. That asymmetry is deliberate: it lets you
re-register a repository elsewhere, or hand it to another cluster,
without losing the backups.

See [`08_cleanup.sh`](./08_cleanup.sh)

## Discussion

### Snapshots are incremental

The first snapshot of an index copies all of its underlying Lucene segment
files into the repository. Every later snapshot copies **only the segments
that changed since the previous snapshot** and references the unchanged
ones. This makes recurring snapshots fast and cheap on disk, yet each
snapshot still restores as a complete, standalone copy. The flip side:
deleting a snapshot only frees the segments that no other snapshot still
needs, because snapshots share data.

### Why snapshots beat copying files

Never back up Elasticsearch by running `cp` or `tar` over the `data/`
directory. Lucene segments are written and merged continuously, so a file
copy of a live index is almost always inconsistent and corrupt on restore.
Snapshots are taken through Elasticsearch itself, are atomic and
point-in-time consistent per shard, are incremental, can be restored into
a different cluster, and are the only Elastic-supported backup method.

### RPO and RTO

Two numbers drive a backup strategy:

- **RPO (Recovery Point Objective)** - how much data you can afford to
  lose, measured in time. It is bounded by how often you snapshot. Hourly
  snapshots give roughly a one-hour RPO; daily snapshots, a one-day RPO.
- **RTO (Recovery Time Objective)** - how long a restore is allowed to
  take. It is driven by data size, repository read throughput and shard
  count. Measure it during a real drill so you can promise a realistic
  number.

Choose a snapshot frequency from your RPO target, and size/validate your
repository and restore process against your RTO target.

### Snapshot Lifecycle Management (SLM)

SLM moves the schedule and retention into Elasticsearch so you do not rely
on external cron jobs. A policy bundles a cron schedule, a snapshot name
template, the repository, the snapshot config, and a retention rule
(`expire_after`, `min_count`, `max_count`). Elasticsearch runs the
snapshots and prunes old ones for you. Monitor `GET /_slm/policy/<name>`
for `last_success` / `last_failure` and `GET /_slm/stats` for failure
counts, and alert when they regress.

### DR best practices

- **Test restores, not just backups.** Run the DR drill on a schedule. A
  backup is only proven when a restore succeeds.
- **Store snapshots off the cluster.** A repository on the same disks as
  your data offers no protection against that hardware failing. In
  production prefer object storage (S3, GCS, Azure) over a local `fs`
  repo; this exercise uses `fs` only because it needs no credentials.
- **Keep multiple generations.** Retention with `min_count` guards against
  a corrupted-data snapshot overwriting your only good copy.
- **Snapshot the global state** when you need cluster settings, templates,
  ILM policies and ingest pipelines back too.
- **Document and rehearse the runbook** so any on-call DBA can restore
  under pressure.
- **Watch repository health** with `POST /_snapshot/<repo>/_verify` and the
  repository analysis API before you depend on it.

## Challenge Exercises

1. Point `06_dr_drill.py` at a real production-like index and measure the
   restore time. That number is your RTO for that index.
1. Change the SLM policy to run hourly and verify the retention rule prunes
   correctly by leaving it running and listing snapshots over time.
1. Take a snapshot, index more documents, take a second snapshot, and use
   `_status` to confirm the second snapshot processed far fewer bytes
   (incremental behaviour).
1. Restore a snapshot into a *different* cluster to simulate full
   cluster-loss recovery.

## Next Steps

1. Replace the `fs` repository with an S3 / GCS / Azure repository plugin
   and re-run the exercise against off-host object storage.
1. Add SLM alerting: watch `_slm/stats` and the policy `last_failure` and
   fire an alert when a scheduled snapshot fails.
1. Combine snapshots with Index Lifecycle Management (see the
   [ILM exercise](../18_index_lifecycle_management/exercise.md)) so
   warm/cold indices are snapshotted before deletion.
1. Practice a partial restore of a single shard that failed, and a restore
   that renames and reduces replicas for a smaller recovery cluster.
