#!/usr/bin/env python3
"""
Elasticsearch Bulk Insert with Performance Measurements
Tests bulk insert performance with indexed vs non-indexed data
"""

import json
import time
import argparse
from datetime import datetime
from elasticsearch import Elasticsearch, helpers
import os
import sys

class BulkInsertTester:
    def __init__(self, es_host='localhost', es_port=9200, es_user='elastic', es_password='changeme'):
        """Initialize Elasticsearch connection"""
        self.es = Elasticsearch(
            [{'host': es_host, 'port': es_port, 'scheme': 'http'}],
            basic_auth=(es_user, es_password),
            verify_certs=False,
            request_timeout=60
        )

        # Test connection
        if not self.es.ping():
            print("Error: Could not connect to Elasticsearch")
            sys.exit(1)

        print(f"Connected to Elasticsearch at {es_host}:{es_port}")

    def create_index_with_mappings(self, index_name, enable_indexing=True):
        """Create index with specified mapping settings"""

        # Delete index if it exists
        if self.es.indices.exists(index=index_name):
            print(f"Deleting existing index: {index_name}")
            self.es.indices.delete(index=index_name)

        # Define mappings based on whether indexing is enabled
        if enable_indexing:
            # Standard indexed mapping
            mappings = {
                "properties": {
                    "product_id": {"type": "keyword"},
                    "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "description": {"type": "text"},
                    "category": {"type": "keyword"},
                    "brand": {"type": "keyword"},
                    "price": {"type": "float"},
                    "stock_quantity": {"type": "integer"},
                    "in_stock": {"type": "boolean"},
                    "rating": {"type": "float"},
                    "review_count": {"type": "integer"},
                    "tags": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "sku": {"type": "keyword"},
                    "weight_kg": {"type": "float"},
                    "is_featured": {"type": "boolean"},
                    "discount_percentage": {"type": "integer"}
                }
            }
            settings = {
                "number_of_shards": 2,
                "number_of_replicas": 1,
                "refresh_interval": "1s"
            }
        else:
            # Minimal indexing - most fields not indexed for search
            mappings = {
                "properties": {
                    "product_id": {"type": "keyword"},
                    "name": {"type": "text", "index": False},
                    "description": {"type": "text", "index": False},
                    "category": {"type": "keyword", "index": False},
                    "brand": {"type": "keyword", "index": False},
                    "price": {"type": "float", "index": False},
                    "stock_quantity": {"type": "integer", "index": False},
                    "in_stock": {"type": "boolean", "index": False},
                    "rating": {"type": "float", "index": False},
                    "review_count": {"type": "integer", "index": False},
                    "tags": {"type": "keyword", "index": False},
                    "created_at": {"type": "date", "index": False},
                    "updated_at": {"type": "date", "index": False},
                    "sku": {"type": "keyword"},
                    "weight_kg": {"type": "float", "index": False},
                    "is_featured": {"type": "boolean", "index": False},
                    "discount_percentage": {"type": "integer", "index": False}
                }
            }
            settings = {
                "number_of_shards": 2,
                "number_of_replicas": 0,
                "refresh_interval": "-1"  # Disable refresh for better bulk performance
            }

        # Create index
        self.es.indices.create(
            index=index_name,
            body={
                "settings": settings,
                "mappings": mappings
            }
        )
        print(f"Created index: {index_name} (indexing={'enabled' if enable_indexing else 'disabled'})")

    def load_data_from_file(self, filename):
        """Load data from NDJSON file"""
        data = []
        with open(filename, 'r') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return data

    def bulk_insert_with_helpers(self, index_name, data, chunk_size=500):
        """Perform bulk insert using Elasticsearch helpers"""

        # Prepare documents for bulk insert
        actions = [
            {
                "_index": index_name,
                "_source": doc
            }
            for doc in data
        ]

        # Measure time
        start_time = time.time()

        # Perform bulk insert
        success, failed = helpers.bulk(
            self.es,
            actions,
            chunk_size=chunk_size,
            request_timeout=60,
            raise_on_error=False
        )

        end_time = time.time()
        elapsed_time = end_time - start_time

        return {
            "success": success,
            "failed": len(failed) if isinstance(failed, list) else 0,
            "elapsed_time": elapsed_time,
            "docs_per_second": success / elapsed_time if elapsed_time > 0 else 0
        }

    def bulk_insert_raw(self, index_name, bulk_file):
        """Perform bulk insert using raw bulk API"""

        # Read bulk formatted file
        with open(bulk_file, 'r') as f:
            bulk_data = f.read()

        start_time = time.time()

        # Execute bulk request
        response = self.es.bulk(body=bulk_data, index=index_name)

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Count successes and failures
        success = 0
        failed = 0
        for item in response['items']:
            if 'index' in item:
                if item['index'].get('status', 0) < 300:
                    success += 1
                else:
                    failed += 1

        return {
            "success": success,
            "failed": failed,
            "elapsed_time": elapsed_time,
            "docs_per_second": success / elapsed_time if elapsed_time > 0 else 0
        }

    def test_bulk_performance(self, data_file, test_name, enable_indexing=True, chunk_sizes=[100, 500, 1000, 5000]):
        """Test bulk insert performance with different chunk sizes"""

        print(f"\n{'='*60}")
        print(f"Test: {test_name}")
        print(f"Indexing: {'Enabled' if enable_indexing else 'Disabled'}")
        print(f"{'='*60}")

        # Load data
        print(f"\nLoading data from {data_file}...")
        data = self.load_data_from_file(data_file)
        print(f"Loaded {len(data)} documents")

        results = []

        for chunk_size in chunk_sizes:
            index_name = f"perf_test_{chunk_size}_{int(time.time())}"

            print(f"\nTesting chunk size: {chunk_size}")

            # Create index
            self.create_index_with_mappings(index_name, enable_indexing)

            # Perform bulk insert
            result = self.bulk_insert_with_helpers(index_name, data, chunk_size)

            # Add metadata
            result['chunk_size'] = chunk_size
            result['total_docs'] = len(data)
            result['index_name'] = index_name
            result['indexing_enabled'] = enable_indexing

            results.append(result)

            # Print results
            print(f"  Documents inserted: {result['success']}")
            print(f"  Failed: {result['failed']}")
            print(f"  Time elapsed: {result['elapsed_time']:.2f} seconds")
            print(f"  Throughput: {result['docs_per_second']:.0f} docs/second")

            # Get index stats
            stats = self.es.indices.stats(index=index_name)
            index_size = stats['indices'][index_name]['total']['store']['size_in_bytes']
            print(f"  Index size: {index_size / (1024*1024):.2f} MB")

            # Clean up
            self.es.indices.delete(index=index_name)

        return results

    def compare_indexing_performance(self, data_file):
        """Compare performance between indexed and non-indexed data"""

        print("\n" + "="*70)
        print("PERFORMANCE COMPARISON: INDEXED vs NON-INDEXED")
        print("="*70)

        # Test with indexing enabled
        indexed_results = self.test_bulk_performance(
            data_file,
            "With Full Indexing",
            enable_indexing=True,
            chunk_sizes=[500, 1000, 5000]
        )

        # Test with indexing disabled
        non_indexed_results = self.test_bulk_performance(
            data_file,
            "Without Indexing",
            enable_indexing=False,
            chunk_sizes=[500, 1000, 5000]
        )

        # Print comparison summary
        print("\n" + "="*70)
        print("SUMMARY COMPARISON")
        print("="*70)
        print(f"\n{'Chunk Size':<12} {'Indexed (docs/s)':<20} {'Non-Indexed (docs/s)':<20} {'Speed Difference':<15}")
        print("-"*70)

        for i, chunk_size in enumerate([500, 1000, 5000]):
            indexed_speed = indexed_results[i]['docs_per_second']
            non_indexed_speed = non_indexed_results[i]['docs_per_second']
            speed_diff = ((non_indexed_speed - indexed_speed) / indexed_speed * 100) if indexed_speed > 0 else 0

            print(f"{chunk_size:<12} {indexed_speed:<20.0f} {non_indexed_speed:<20.0f} {speed_diff:+.1f}%")

        # Calculate averages
        avg_indexed = sum(r['docs_per_second'] for r in indexed_results) / len(indexed_results)
        avg_non_indexed = sum(r['docs_per_second'] for r in non_indexed_results) / len(non_indexed_results)
        avg_diff = ((avg_non_indexed - avg_indexed) / avg_indexed * 100) if avg_indexed > 0 else 0

        print("-"*70)
        print(f"{'Average':<12} {avg_indexed:<20.0f} {avg_non_indexed:<20.0f} {avg_diff:+.1f}%")

        return indexed_results, non_indexed_results

def main():
    parser = argparse.ArgumentParser(description='Test Elasticsearch bulk insert performance')
    parser.add_argument('--host', default='localhost', help='Elasticsearch host')
    parser.add_argument('--port', type=int, default=9200, help='Elasticsearch port')
    parser.add_argument('--user', default='elastic', help='Elasticsearch username')
    parser.add_argument('--password', default='changeme', help='Elasticsearch password')
    parser.add_argument('--data-file', default='./data/products.ndjson', help='Path to data file')
    parser.add_argument('--test-type', choices=['indexed', 'non-indexed', 'compare'], default='compare',
                       help='Type of test to run')

    args = parser.parse_args()

    # Check if data file exists
    if not os.path.exists(args.data_file):
        print(f"Error: Data file not found: {args.data_file}")
        print("Please run generate_data.py first to create test data")
        sys.exit(1)

    # Initialize tester
    tester = BulkInsertTester(args.host, args.port, args.user, args.password)

    # Run tests based on type
    if args.test_type == 'indexed':
        tester.test_bulk_performance(args.data_file, "Indexed Data Test", enable_indexing=True)
    elif args.test_type == 'non-indexed':
        tester.test_bulk_performance(args.data_file, "Non-Indexed Data Test", enable_indexing=False)
    else:  # compare
        tester.compare_indexing_performance(args.data_file)

    print("\n✓ Performance testing complete!")

if __name__ == "__main__":
    main()