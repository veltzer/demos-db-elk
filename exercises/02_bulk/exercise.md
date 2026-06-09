# Elasticsearch Bulk Insert Performance Exercise

This exercise demonstrates bulk data insertion into Elasticsearch and
compares performance between indexed and non-indexed data configurations.

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

See [`01_check_elasticsearch_status.sh`](./01_check_elasticsearch_status.sh)

## Quick Start

### Step 1: Generate Test Data

See [`02_generate_test_data.sh`](./02_generate_test_data.sh)

### Step 2: Run Basic Bulk Insert Test

See [`03_run_bulk_insert_test.sh`](./03_run_bulk_insert_test.sh)

### Step 3: Run Comprehensive Performance Tests

See [`04_run_performance_suite.sh`](./04_run_performance_suite.sh)

## Understanding the Results

### Performance Configurations Tested

1. **Standard**: Normal Elasticsearch settings with full indexing
1. **Bulk Optimized**: Optimized settings for bulk loading (disabled refresh,
   async translog)
1. **Minimal Indexing**: Only essential fields indexed
1. **No Indexing**: Most fields stored but not indexed (fastest insertion)

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
1. **Reduce Replicas**: Set `number_of_replicas` to 0 during bulk load
1. **Increase Bulk Size**: Use larger chunk sizes (5000-10000 documents)
1. **Disable Indexing**: Only index fields you need to search

### Example: Optimized Bulk Loading

See [`05_bulk_optimized_index_setup.py`](./05_bulk_optimized_index_setup.py)

## Troubleshooting

### Connection Issues

If you get connection errors:
See [`06_check_connection.sh`](./06_check_connection.sh)

### Memory Issues

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
