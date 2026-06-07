# Elasticsearch Bulk Insert Performance Exercise

This exercise demonstrates bulk data insertion into Elasticsearch and compares performance between indexed and non-indexed data configurations.

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

See [`02_bulk_01.sh`](./02_bulk_01.sh)


## Quick Start

### Step 1: Generate Test Data

See [`02_bulk_02.sh`](./02_bulk_02.sh)


### Step 2: Run Basic Bulk Insert Test

See [`02_bulk_03.sh`](./02_bulk_03.sh)


### Step 3: Run Comprehensive Performance Tests

See [`02_bulk_04.sh`](./02_bulk_04.sh)


## Understanding the Results

### Performance Configurations Tested

1. **Standard**: Normal Elasticsearch settings with full indexing
2. **Bulk Optimized**: Optimized settings for bulk loading (disabled refresh, async translog)
3. **Minimal Indexing**: Only essential fields indexed
4. **No Indexing**: Most fields stored but not indexed (fastest insertion)

### Key Metrics

- **Documents/Second**: Throughput of bulk insertion
- **Index Size**: Storage space used
- **Efficiency**: Documents per second per MB of storage

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
2. **Reduce Replicas**: Set `number_of_replicas` to 0 during bulk load
3. **Increase Bulk Size**: Use larger chunk sizes (5000-10000 documents)
4. **Disable Indexing**: Only index fields you need to search

### Example: Optimized Bulk Loading

See [`02_bulk_01.py`](./02_bulk_01.py)


## Troubleshooting

### Connection Issues

If you get connection errors:
See [`02_bulk_05.sh`](./02_bulk_05.sh)


### Memory Issues

For large datasets, increase heap size:
See [`02_bulk_06.sh`](./02_bulk_06.sh)


### Slow Performance

1. Check disk I/O: `iostat -x 1`
2. Monitor Elasticsearch: `GET /_nodes/stats`
3. Reduce chunk size if getting timeouts
4. Ensure sufficient disk space

## Advanced Usage

### Custom Data Generation

See [`02_bulk_08.sh`](./02_bulk_08.sh)


### Parallel Bulk Loading

For very large datasets, split files and load in parallel:

See [`02_bulk_07.sh`](./02_bulk_07.sh)


## Learning Objectives

By completing this exercise, you'll understand:

1. **Bulk API Usage**: How to efficiently insert large amounts of data
2. **Index Settings Impact**: How settings affect insertion performance
3. **Indexing vs Storage**: Trade-offs between searchability and insert speed
4. **Performance Tuning**: Techniques to optimize bulk operations
5. **Monitoring**: How to measure and analyze performance

## Next Steps

1. Try different mapping configurations
2. Test with real-world data patterns
3. Implement error handling and retry logic
4. Explore parallel processing strategies
5. Test with cluster configurations (multiple nodes)
