#!/usr/bin/env python3
"""
Complete Performance Testing Suite for Elasticsearch Bulk Insert
Measures and compares bulk insert performance with various configurations
"""

import json
import time
import argparse
import os
import sys
from datetime import datetime
from elasticsearch import Elasticsearch, helpers
import matplotlib.pyplot as plt
import numpy as np

class PerformanceTestSuite:
    def __init__(self, es_host='localhost', es_port=9200, es_user='elastic', es_password='changeme'):
        """Initialize test suite"""
        self.es = Elasticsearch(
            [{'host': es_host, 'port': es_port, 'scheme': 'http'}],
            basic_auth=(es_user, es_password),
            verify_certs=False,
            request_timeout=120
        )

        if not self.es.ping():
            print("Error: Could not connect to Elasticsearch")
            sys.exit(1)

        print(f"✓ Connected to Elasticsearch at {es_host}:{es_port}")
        self.results = []

    def create_optimized_index(self, index_name, config_type='standard'):
        """Create index with different optimization configurations"""

        if self.es.indices.exists(index=index_name):
            self.es.indices.delete(index=index_name)

        configs = {
            'standard': {
                'settings': {
                    'number_of_shards': 2,
                    'number_of_replicas': 1,
                    'refresh_interval': '1s'
                },
                'mappings': self._get_standard_mappings()
            },
            'bulk_optimized': {
                'settings': {
                    'number_of_shards': 2,
                    'number_of_replicas': 0,
                    'refresh_interval': '-1',
                    'index.translog.durability': 'async',
                    'index.translog.sync_interval': '30s'
                },
                'mappings': self._get_standard_mappings()
            },
            'minimal_indexing': {
                'settings': {
                    'number_of_shards': 1,
                    'number_of_replicas': 0,
                    'refresh_interval': '-1'
                },
                'mappings': self._get_minimal_mappings()
            },
            'no_indexing': {
                'settings': {
                    'number_of_shards': 1,
                    'number_of_replicas': 0,
                    'refresh_interval': '-1'
                },
                'mappings': self._get_no_index_mappings()
            }
        }

        config = configs.get(config_type, configs['standard'])
        self.es.indices.create(index=index_name, body=config)

    def _get_standard_mappings(self):
        """Standard mapping with full indexing"""
        return {
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
                "updated_at": {"type": "date"}
            }
        }

    def _get_minimal_mappings(self):
        """Minimal mapping with selective indexing"""
        return {
            "properties": {
                "product_id": {"type": "keyword"},
                "name": {"type": "text"},
                "category": {"type": "keyword"},
                "price": {"type": "float"},
                "in_stock": {"type": "boolean"}
            },
            "dynamic": "false"
        }

    def _get_no_index_mappings(self):
        """Mapping with indexing disabled for most fields"""
        return {
            "properties": {
                "product_id": {"type": "keyword"},
                "name": {"type": "text", "index": False},
                "description": {"type": "text", "index": False},
                "category": {"type": "keyword", "index": False},
                "brand": {"type": "keyword", "index": False},
                "price": {"type": "float", "index": False},
                "stock_quantity": {"type": "integer", "index": False},
                "in_stock": {"type": "boolean", "index": False}
            },
            "dynamic": "false"
        }

    def load_test_data(self, filename, limit=None):
        """Load test data from file"""
        data = []
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                if limit and i >= limit:
                    break
                if line.strip():
                    data.append(json.loads(line))
        return data

    def measure_bulk_insert(self, index_name, data, chunk_size=1000, config_type='standard'):
        """Measure bulk insert performance"""

        # Create index with specified configuration
        self.create_optimized_index(index_name, config_type)

        # Prepare bulk actions
        actions = [
            {
                "_index": index_name,
                "_source": doc
            }
            for doc in data
        ]

        # Start measurement
        start_time = time.time()
        start_memory = self._get_index_memory(index_name)

        # Perform bulk insert
        success_count = 0
        failed_count = 0

        for i in range(0, len(actions), chunk_size):
            batch = actions[i:i + chunk_size]
            try:
                success, failed = helpers.bulk(
                    self.es,
                    batch,
                    request_timeout=60,
                    raise_on_error=False
                )
                success_count += success
                if isinstance(failed, list):
                    failed_count += len(failed)
            except Exception as e:
                print(f"Error in batch {i//chunk_size}: {e}")
                failed_count += len(batch)

        # End measurement
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Force refresh to get accurate stats
        self.es.indices.refresh(index=index_name)

        # Get final stats
        stats = self.es.indices.stats(index=index_name)
        doc_count = stats['indices'][index_name]['primaries']['docs']['count']
        index_size = stats['indices'][index_name]['primaries']['store']['size_in_bytes']

        result = {
            'config_type': config_type,
            'chunk_size': chunk_size,
            'total_docs': len(data),
            'success_count': success_count,
            'failed_count': failed_count,
            'elapsed_time': elapsed_time,
            'docs_per_second': success_count / elapsed_time if elapsed_time > 0 else 0,
            'index_size_mb': index_size / (1024 * 1024),
            'bytes_per_doc': index_size / doc_count if doc_count > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }

        # Clean up
        self.es.indices.delete(index=index_name)

        return result

    def _get_index_memory(self, index_name):
        """Get current index memory usage"""
        try:
            stats = self.es.indices.stats(index=index_name)
            return stats['indices'][index_name]['primaries']['store']['size_in_bytes']
        except:
            return 0

    def run_comprehensive_test(self, data_file, test_sizes=[1000, 5000, 10000]):
        """Run comprehensive performance tests"""

        print("\n" + "="*70)
        print("COMPREHENSIVE BULK INSERT PERFORMANCE TEST")
        print("="*70)

        all_results = []

        # Test different configurations
        configs = ['standard', 'bulk_optimized', 'minimal_indexing', 'no_indexing']
        chunk_sizes = [500, 1000, 5000]

        for test_size in test_sizes:
            print(f"\n\nTesting with {test_size} documents")
            print("-"*50)

            # Load data
            data = self.load_test_data(data_file, limit=test_size)

            for config in configs:
                for chunk_size in chunk_sizes:
                    print(f"\nConfig: {config:20} Chunk: {chunk_size:5} Docs: {test_size:6}")

                    index_name = f"perf_{config}_{chunk_size}_{int(time.time())}"
                    result = self.measure_bulk_insert(index_name, data, chunk_size, config)

                    all_results.append(result)

                    print(f"  Time: {result['elapsed_time']:6.2f}s")
                    print(f"  Speed: {result['docs_per_second']:6.0f} docs/s")
                    print(f"  Size: {result['index_size_mb']:6.2f} MB")

        return all_results

    def generate_report(self, results, output_dir='./results'):
        """Generate performance report with visualizations"""

        os.makedirs(output_dir, exist_ok=True)

        # Group results by configuration
        configs = {}
        for r in results:
            config = r['config_type']
            if config not in configs:
                configs[config] = []
            configs[config].append(r)

        # Create performance comparison chart
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Elasticsearch Bulk Insert Performance Analysis', fontsize=16)

        # Chart 1: Throughput comparison
        ax1 = axes[0, 0]
        for config, data in configs.items():
            sizes = [d['total_docs'] for d in data]
            speeds = [d['docs_per_second'] for d in data]
            ax1.plot(sizes, speeds, marker='o', label=config)
        ax1.set_xlabel('Document Count')
        ax1.set_ylabel('Documents/Second')
        ax1.set_title('Throughput by Configuration')
        ax1.legend()
        ax1.grid(True)

        # Chart 2: Time comparison
        ax2 = axes[0, 1]
        config_names = list(configs.keys())
        avg_times = [np.mean([d['elapsed_time'] for d in data]) for data in configs.values()]
        bars = ax2.bar(config_names, avg_times)
        ax2.set_ylabel('Average Time (seconds)')
        ax2.set_title('Average Insert Time by Configuration')
        ax2.grid(True, axis='y')

        # Add value labels on bars
        for bar, time in zip(bars, avg_times):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{time:.1f}s', ha='center', va='bottom')

        # Chart 3: Index size comparison
        ax3 = axes[1, 0]
        avg_sizes = [np.mean([d['index_size_mb'] for d in data]) for data in configs.values()]
        bars = ax3.bar(config_names, avg_sizes)
        ax3.set_ylabel('Index Size (MB)')
        ax3.set_title('Average Index Size by Configuration')
        ax3.grid(True, axis='y')

        # Chart 4: Efficiency (docs/s per MB)
        ax4 = axes[1, 1]
        efficiencies = []
        for config, data in configs.items():
            efficiency = np.mean([d['docs_per_second'] / d['index_size_mb']
                                 if d['index_size_mb'] > 0 else 0 for d in data])
            efficiencies.append(efficiency)
        bars = ax4.bar(config_names, efficiencies)
        ax4.set_ylabel('Docs/s per MB')
        ax4.set_title('Storage Efficiency by Configuration')
        ax4.grid(True, axis='y')

        plt.tight_layout()
        plt.savefig(f'{output_dir}/performance_analysis.png', dpi=100)
        plt.close()

        # Generate text report
        report_file = f'{output_dir}/performance_report.txt'
        with open(report_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("ELASTICSEARCH BULK INSERT PERFORMANCE REPORT\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("="*70 + "\n\n")

            for config, data in configs.items():
                f.write(f"\nConfiguration: {config.upper()}\n")
                f.write("-"*40 + "\n")

                avg_speed = np.mean([d['docs_per_second'] for d in data])
                avg_time = np.mean([d['elapsed_time'] for d in data])
                avg_size = np.mean([d['index_size_mb'] for d in data])
                max_speed = max([d['docs_per_second'] for d in data])
                min_speed = min([d['docs_per_second'] for d in data])

                f.write(f"  Average Speed: {avg_speed:.0f} docs/second\n")
                f.write(f"  Speed Range: {min_speed:.0f} - {max_speed:.0f} docs/second\n")
                f.write(f"  Average Time: {avg_time:.2f} seconds\n")
                f.write(f"  Average Index Size: {avg_size:.2f} MB\n")
                f.write(f"  Tests Run: {len(data)}\n")

            # Summary comparison
            f.write("\n" + "="*70 + "\n")
            f.write("PERFORMANCE COMPARISON SUMMARY\n")
            f.write("="*70 + "\n\n")

            # Find best configuration for speed
            best_speed_config = max(configs.keys(),
                                   key=lambda c: np.mean([d['docs_per_second'] for d in configs[c]]))
            best_speed = np.mean([d['docs_per_second'] for d in configs[best_speed_config]])

            # Find most space-efficient configuration
            best_size_config = min(configs.keys(),
                                  key=lambda c: np.mean([d['index_size_mb'] for d in configs[c]]))
            best_size = np.mean([d['index_size_mb'] for d in configs[best_size_config]])

            f.write(f"Fastest Configuration: {best_speed_config}\n")
            f.write(f"  Average Speed: {best_speed:.0f} docs/second\n\n")

            f.write(f"Most Space-Efficient: {best_size_config}\n")
            f.write(f"  Average Size: {best_size:.2f} MB\n\n")

            # Performance improvement analysis
            standard_speed = np.mean([d['docs_per_second'] for d in configs.get('standard', [])])
            if standard_speed > 0:
                f.write("Performance Improvements vs Standard Configuration:\n")
                for config in configs:
                    if config != 'standard':
                        config_speed = np.mean([d['docs_per_second'] for d in configs[config]])
                        improvement = ((config_speed - standard_speed) / standard_speed) * 100
                        f.write(f"  {config}: {improvement:+.1f}%\n")

        print(f"\n✓ Report generated: {report_file}")
        print(f"✓ Chart saved: {output_dir}/performance_analysis.png")

        return report_file

def main():
    parser = argparse.ArgumentParser(description='Run comprehensive Elasticsearch bulk insert performance tests')
    parser.add_argument('--host', default='localhost', help='Elasticsearch host')
    parser.add_argument('--port', type=int, default=9200, help='Elasticsearch port')
    parser.add_argument('--user', default='elastic', help='Elasticsearch username')
    parser.add_argument('--password', default='changeme', help='Elasticsearch password')
    parser.add_argument('--data-file', default='./data/products.ndjson', help='Path to data file')
    parser.add_argument('--test-sizes', nargs='+', type=int, default=[1000, 5000, 10000],
                       help='Document counts to test')
    parser.add_argument('--output-dir', default='./results', help='Output directory for results')

    args = parser.parse_args()

    # Check data file
    if not os.path.exists(args.data_file):
        print(f"Error: Data file not found: {args.data_file}")
        print("Please run: python generate_data.py")
        sys.exit(1)

    # Initialize test suite
    suite = PerformanceTestSuite(args.host, args.port, args.user, args.password)

    # Run comprehensive tests
    results = suite.run_comprehensive_test(args.data_file, args.test_sizes)

    # Generate report
    suite.generate_report(results, args.output_dir)

    # Save raw results as JSON
    results_file = f"{args.output_dir}/raw_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"✓ Raw results saved: {results_file}")

    print("\n✓ All tests complete!")

if __name__ == "__main__":
    main()