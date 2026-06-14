# Elasticsearch Bulk Insert Performance Exercise

This exercise demonstrates bulk data insertion into Elasticsearch and
compares performance between indexed and non-indexed data configurations.

Why bulk matters: sending documents to Elasticsearch one at a time means
one HTTP request per document. Each request pays the cost of network
round trips, request parsing, and per-call overhead. The Bulk API packs
many operations into a single request, so the fixed costs are paid once
for hundreds or thousands of documents. This is the single biggest lever
for ingestion throughput, and everything else in this exercise builds on
top of it.

The second theme is the tension between write speed and search
readiness. Elasticsearch is built on Lucene, which turns text into
inverted indexes so that searches are fast. Building those structures
costs time during writes. When you index less, you write faster but can
search less. This exercise lets you measure that trade-off directly.

## Overview

The exercise includes:

- Fake e-commerce data generation
- Bulk insert implementation with different strategies
- Performance comparison between indexed vs non-indexed configurations
- Comprehensive performance testing and reporting

## Files

- `generate_data.py` - Generates fake e-commerce data (products, customers, orders)
- `bulk_insert.py` - Performs bulk inserts with performance measurements
- `run_performance_test.py` - Comprehensive performance testing suite with visualizations
- `exercise.md` - Original exercise instructions

## Prerequisites

### 1. Install Python Dependencies

```bash
pip install elasticsearch faker matplotlib numpy
```

### 2. Ensure Elasticsearch is Running

A quick request to the root URL is the simplest health check. A running
node replies with a small JSON document describing its name, cluster, and
version. If you get a connection refused error, the service is not up
yet, and none of the steps below will work.

See [`01_check_elasticsearch_status.sh`](./01_check_elasticsearch_status.sh)

## Quick Start

### Step 1: Generate Test Data

Real ingestion tuning needs realistic volumes, so the first step creates
synthetic e-commerce records. The data is written in NDJSON, which means
newline-delimited JSON: one complete JSON object per line. This format
maps directly onto how the Bulk API expects to receive data, and it lets
you stream a file line by line instead of loading it all into memory.

See [`02_generate_test_data.sh`](./02_generate_test_data.sh)

### Step 2: Run Basic Bulk Insert Test

This step pushes the generated documents through the Bulk API and times
the result. Under the hood it uses the Python client helper that batches
documents into chunks and sends each chunk as one bulk request. The test
runs both an indexed and a non-indexed configuration so you can see the
difference in documents per second side by side.

See [`03_run_bulk_insert_test.sh`](./03_run_bulk_insert_test.sh)

### Step 3: Run Comprehensive Performance Tests

The full suite repeats the load across several batch sizes and index
configurations, then writes charts and a report. Running many points lets
you find the sweet spot rather than guessing: throughput usually climbs
with batch size, then flattens or drops once batches get so large they
strain memory and trigger timeouts.

See [`04_run_performance_suite.sh`](./04_run_performance_suite.sh)

## Understanding the Results

### Performance Configurations Tested

Each configuration trades some search capability or durability for write
speed. Reading them top to bottom is a tour from safe defaults toward
maximum raw throughput.

1. **Standard**: Normal Elasticsearch settings with full indexing
1. **Bulk Optimized**: Optimized settings for bulk loading (disabled refresh,
   async translog)
1. **Minimal Indexing**: Only essential fields indexed
1. **No Indexing**: Most fields stored but not indexed (fastest insertion)

What the settings mean. The refresh interval controls how often newly
written documents become visible to search. A refresh creates a new
Lucene segment, which is real work, so disabling it during a load avoids
that cost and lets you do one refresh at the end. The translog is the
write-ahead log that makes writes durable; flushing it less aggressively
speeds writes at the price of a small window of risk if the node crashes.
Replicas multiply write work, since every document is also copied to its
replica shards, so dropping replicas to zero during a load and adding
them back afterward is a common pattern.

### Key Metrics

- **Documents/Second**: Throughput of bulk insertion
- **Index Size**: Storage space used
- **Efficiency**: Documents per second per MB of storage

Why look at all three together. Throughput alone can mislead you. A
configuration that indexes almost nothing will write quickly, but it also
produces a smaller index because it skips building the inverted index
structures, and it can answer fewer queries. The efficiency metric ties
speed and size together so you can compare configurations fairly rather
than optimizing one number at the expense of the others.

### Expected Results

Typical performance improvements:

- **No Indexing**: 50-100% faster than standard
- **Bulk Optimized**: 30-50% faster than standard
- **Minimal Indexing**: 20-40% faster than standard

## Output Files

After running tests, you'll find:

```
./data/
  ├── products.ndjson       # Generated product data
  ├── customers.ndjson      # Generated customer data
  └── orders.ndjson         # Generated order data

./results/
  ├── performance_analysis.png   # Performance charts
  ├── performance_report.txt     # Detailed text report
  └── raw_results.json          # Raw test results
```

## Optimization Tips

### For Maximum Insert Speed

1. **Disable Refresh**: Set `refresh_interval` to `-1`
1. **Reduce Replicas**: Set `number_of_replicas` to 0 during bulk load
1. **Increase Bulk Size**: Use larger chunk sizes (5000-10000 documents)
1. **Disable Indexing**: Only index fields you need to search

A note on chunk size. There is no single best value. Too small and you
pay request overhead too often; too large and a single request can
exceed memory limits or time out, forcing retries that hurt throughput.
The right number depends on document size and node resources, which is
exactly why the suite sweeps several values and lets the data decide.

### Example: Optimized Bulk Loading

The pattern below is the safe way to apply these tips: create the index
with replicas off and refresh disabled, run the bulk load, then restore
normal settings and trigger one final refresh so the data becomes
searchable and properly replicated. Doing it in this order means you get
the speed during the load without permanently sacrificing durability or
search visibility.

See [`05_bulk_optimized_index_setup.py`](./05_bulk_optimized_index_setup.py)

## Troubleshooting

### Connection Issues

If you get connection errors:
See [`06_check_connection.sh`](./06_check_connection.sh)

### Memory Issues

Bulk requests are held in memory while a node parses and applies them, so
large batches on an undersized heap can lead to memory pressure and slow,
unstable behavior. Raising the heap gives the node room to work. A common
guideline is to set the minimum and maximum heap to the same value so the
JVM does not spend time resizing, and to keep it well under half of the
machine's physical memory so the operating system can cache index files.

For large datasets, increase heap size:
See [`07_increase_heap_size.sh`](./07_increase_heap_size.sh)

### Slow Performance

1. Check disk I/O: `iostat -x 1`
1. Monitor Elasticsearch: `GET /_nodes/stats`
1. Reduce chunk size if getting timeouts
1. Ensure sufficient disk space

## Advanced Usage

### Custom Data Generation

See [`08_generate_products_only.sh`](./08_generate_products_only.sh)

### Parallel Bulk Loading

A single client sending one bulk request at a time often cannot keep a
multi-core cluster busy. Splitting the input and running several loaders
at once lets the cluster apply work in parallel across shards and CPUs.
The catch is that more parallelism is not always faster: past the point
where the cluster is saturated, extra loaders just add contention and
rejected requests. Increase concurrency gradually and watch throughput.

For very large datasets, split files and load in parallel:

See [`09_parallel_bulk_load.sh`](./09_parallel_bulk_load.sh)

## Learning Objectives

By completing this exercise, you'll understand:

1. **Bulk API Usage**: How to efficiently insert large amounts of data
1. **Index Settings Impact**: How settings affect insertion performance
1. **Indexing vs Storage**: Trade-offs between searchability and insert speed
1. **Performance Tuning**: Techniques to optimize bulk operations
1. **Monitoring**: How to measure and analyze performance

## Next Steps

1. Try different mapping configurations
1. Test with real-world data patterns
1. Implement error handling and retry logic
1. Explore parallel processing strategies
1. Test with cluster configurations (multiple nodes)
