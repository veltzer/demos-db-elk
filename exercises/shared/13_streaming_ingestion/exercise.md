# Elasticsearch Streaming Ingestion Exercise

This exercise demonstrates continuous, one-document-at-a-time ingestion into
Elasticsearch — the pattern behind metrics, sensor readings, log lines and
other time-series data that never stops arriving.

## Overview

Unlike the bulk exercise (which loads a fixed dataset in one shot), here a
producer keeps inserting fresh documents indefinitely. You run the streamer in
one terminal and observe the index growing in another.

**Why this matters.** A huge fraction of real Elasticsearch workloads are
streaming, not batch. Application logs, server metrics, click events and
sensor readings all arrive as an unbounded sequence with no natural end. The
defining trait of a stream is that you can never "finish loading" — the data
keeps coming, so your index must absorb writes continuously while it is also
being read and searched. This exercise gives you the smallest possible version
of that pattern so the moving parts are easy to see: one writer, one reader,
one index.

The exercise includes:

- Creating a typed index for the incoming time-series fields
- A streaming producer that inserts one document per second, forever
- A reader that reports the live document count and the most recent records
- A cleanup step that empties the index without dropping it

## Files

- `01_create_index.sh` - Create the `wpt` index with an explicit mapping
- `02_drop_index.sh` - Drop the `wpt` index
- `stream_data.py` - Continuously insert one document per second (Ctrl-C to stop)
- `show_data.py` - Show the current document count and most recent records
- `remove_data.py` - Delete all documents from the index (keeps the mapping)

## Prerequisites

### 1. Install Python Dependencies

```bash
pip install elasticsearch
```

### 2. Ensure Elasticsearch is Running

Elasticsearch should be reachable on `localhost:9200`. See the
[`00_install`](../00_install/exercise.md) exercise if you have not set it up yet.

## Quick Start

### Step 1: Create the Index

**What's happening.** We create the `wpt` ("web page timings") index up front
with an explicit mapping that types `day` as `integer` and `speed_of_load` as
`float`. If you skipped this and let the first streamed document define the
schema, Elasticsearch would guess the types through *dynamic mapping*. That
guessing is the common pitfall in streaming pipelines: a value that happens to
look like a string in the first document locks the field to `text` forever,
and you cannot change a field's type without reindexing. Declaring the mapping
before any data arrives removes that risk and guarantees every streamed
document is stored and queried the same way.

The index is created with a single shard and zero replicas. A *shard* is the
unit of storage and parallelism in Elasticsearch; a *replica* is a redundant
copy on another node for fault tolerance. For a single-node training cluster
one shard and no replicas is ideal — replicas would stay unassigned with
nowhere to go, leaving the cluster health yellow.

See [`01_create_index.sh`](./01_create_index.sh)

### Step 2: Start Streaming

In one terminal, start the producer. It inserts a record every second and
keeps going until you press Ctrl-C:

```bash
./stream_data.py
```

**What's happening.** Each loop builds one small document and sends it with a
single `index` call. Because no document id is supplied, Elasticsearch
generates one automatically — this is the right choice for append-only stream
data, since every event is new and you never want to overwrite a previous one.
The producer also checks `result["_shards"]["successful"] >= 1`, which
confirms the write was durably accepted by at least one shard before moving on.

Sending documents one at a time is deliberately the slowest, simplest path.
Every `index` call is a separate HTTP request with its own round trip, so
throughput is limited to roughly one document per second here only because we
sleep on purpose. The point is the mental model, not the speed; the Discussion
below explains when you would switch to batching.

### Step 3: Watch the Data Grow

In a second terminal, run the reader a few times and watch the total climb:

```bash
./show_data.py
```

### Step 4: Clean Up

Stop the producer with Ctrl-C, then empty the index:

```bash
./remove_data.py
```

To remove the index entirely, see
[`02_drop_index.sh`](./02_drop_index.sh).

## Discussion

- **Why one-at-a-time?** This mirrors a live feed where you cannot wait to batch
  documents. In production you would usually buffer and use the bulk API (see
  the [`02_bulk`](../02_bulk/exercise.md) exercise) for throughput, but the
  single-document path is the simplest mental model for a stream.
- **Refresh interval.** Newly indexed documents are not searchable until a
  refresh occurs. `show_data.py` calls `indices.refresh` so you always see the
  latest count; in a real stream you would tune `refresh_interval` instead of
  refreshing on every read.
- **Back-pressure and time.** A real producer would carry a real timestamp and
  handle back-pressure when Elasticsearch is slow. Here `day` simply increments
  so you can sort by arrival order.

## Exercises

1. Change `stream_data.py` to attach a real `@timestamp` field and re-run.
1. Make the producer insert in small bulk batches instead of one at a time and
   compare the ingestion rate.
1. Add a second field (for example a random `server_name`) and use
   `show_data.py` to aggregate the average `speed_of_load` per server.
