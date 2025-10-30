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

```bash
# Check Elasticsearch status
curl -X GET "localhost:9200" -u elastic:changeme
```

## Quick Start

### Step 1: Generate Test Data

```bash
# Generate default dataset (10K products, 5K customers, 20K orders)
python generate_data.py

# Generate smaller dataset for quick testing
python generate_data.py --products 1000 --customers 500 --orders 2000

# Generate larger dataset for stress testing
python generate_data.py --products 50000 --customers 10000 --orders 100000
```

### Step 2: Run Basic Bulk Insert Test

```bash
# Compare indexed vs non-indexed performance
python bulk_insert.py --data-file ./data/bulk_products.json

# Test only indexed configuration
python bulk_insert.py --test-type indexed

# Test only non-indexed configuration
python bulk_insert.py --test-type non-indexed
```

### Step 3: Run Comprehensive Performance Tests

```bash
# Run full performance suite with visualizations
python run_performance_test.py

# Test with custom sizes
python run_performance_test.py --test-sizes 1000 5000 10000 25000

# Use custom Elasticsearch credentials
python run_performance_test.py --user elastic --password your-password
```

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

```python
# 1. Create index with bulk-optimized settings
PUT /products
{
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 0,
    "refresh_interval": "-1"
  }
}

# 2. Perform bulk insert
# ... bulk insert operations ...

# 3. Re-enable normal settings after loading
PUT /products/_settings
{
  "number_of_replicas": 1,
  "refresh_interval": "1s"
}
```

## Troubleshooting

### Connection Issues

If you get connection errors:
```bash
# Check Elasticsearch is running
systemctl status elasticsearch

# Test connection
curl -X GET "http://localhost:9200"
```

### Memory Issues

For large datasets, increase heap size:
```bash
# Edit /etc/elasticsearch/jvm.options
-Xms4g
-Xmx4g
```

### Slow Performance

1. Check disk I/O: `iostat -x 1`
2. Monitor Elasticsearch: `GET /_nodes/stats`
3. Reduce chunk size if getting timeouts
4. Ensure sufficient disk space

## Advanced Usage

### Custom Data Generation

```python
# Generate only products with specific settings
python generate_data.py --products 100000 --customers 0 --orders 0 --format ndjson
```

### Parallel Bulk Loading

For very large datasets, split files and load in parallel:

```bash
# Split large file
split -l 10000 products.ndjson products_part_

# Load parts in parallel
for file in products_part_*; do
    python bulk_insert.py --data-file $file &
done
```

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
