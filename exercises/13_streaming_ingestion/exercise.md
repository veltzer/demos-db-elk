# Elasticsearch Streaming Ingestion Exercise

This exercise demonstrates continuous, one-document-at-a-time ingestion into
Elasticsearch — the pattern behind metrics, sensor readings, log lines and
other time-series data that never stops arriving.

## Overview

Unlike the bulk exercise (which loads a fixed dataset in one shot), here a
producer keeps inserting fresh documents indefinitely. You run the streamer in
one terminal and observe the index growing in another.

The exercise includes:

- Creating a typed index for the incoming time-series fields
- A streaming producer that inserts one document per second, forever
- A reader that reports the live document count and the most recent records
- A cleanup step that empties the index without dropping it

## Files

- `13_streaming_ingestion_01.sh` - Create the `wpt` index with an explicit mapping
- `13_streaming_ingestion_02.sh` - Drop the `wpt` index
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

See [`13_streaming_ingestion_01.sh`](./13_streaming_ingestion_01.sh)

### Step 2: Start Streaming

In one terminal, start the producer. It inserts a record every second and
keeps going until you press Ctrl-C:

```bash
./stream_data.py
```

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
[`13_streaming_ingestion_02.sh`](./13_streaming_ingestion_02.sh).

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
