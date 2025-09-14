#!/usr/bin/env python
"""
Script to create fake data for Elasticsearch query performance testing.
Demonstrates the impact of indexing on query performance.
"""

import random
import time
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch, helpers
from faker import Faker
import argparse

fake = Faker()
es = Elasticsearch(['http://localhost:9200'])

def create_indexed_mapping():
    """Create mapping with all fields indexed (default behavior)"""
    return {
        'mappings': {
            'properties': {
                'user_id': {'type': 'keyword'},
                'username': {'type': 'keyword'},
                'email': {'type': 'keyword'},
                'full_name': {
                    'type': 'text',
                    'fields': {
                        'keyword': {'type': 'keyword'}
                    }
                },
                'bio': {'type': 'text'},
                'age': {'type': 'integer'},
                'salary': {'type': 'float'},
                'department': {'type': 'keyword'},
                'job_title': {'type': 'text'},
                'location': {
                    'properties': {
                        'city': {'type': 'keyword'},
                        'country': {'type': 'keyword'},
                        'latitude': {'type': 'float'},
                        'longitude': {'type': 'float'}
                    }
                },
                'joined_date': {'type': 'date'},
                'last_login': {'type': 'date'},
                'is_active': {'type': 'boolean'},
                'tags': {'type': 'keyword'},
                'post_count': {'type': 'integer'},
                'followers': {'type': 'integer'},
                'metadata': {'type': 'text'}
            }
        }
    }

def create_non_indexed_mapping():
    """Create mapping with some fields not indexed for comparison"""
    return {
        'mappings': {
            'properties': {
                'user_id': {'type': 'keyword'},
                'username': {'type': 'keyword'},
                'email': {'type': 'keyword', 'index': False},  # Not indexed
                'full_name': {
                    'type': 'text',
                    'fields': {
                        'keyword': {'type': 'keyword'}
                    }
                },
                'bio': {'type': 'text', 'index': False},  # Not indexed
                'age': {'type': 'integer'},
                'salary': {'type': 'float', 'index': False},  # Not indexed
                'department': {'type': 'keyword'},
                'job_title': {'type': 'text', 'index': False},  # Not indexed
                'location': {
                    'properties': {
                        'city': {'type': 'keyword'},
                        'country': {'type': 'keyword', 'index': False},  # Not indexed
                        'latitude': {'type': 'float', 'index': False},  # Not indexed
                        'longitude': {'type': 'float', 'index': False}  # Not indexed
                    }
                },
                'joined_date': {'type': 'date'},
                'last_login': {'type': 'date', 'index': False},  # Not indexed
                'is_active': {'type': 'boolean'},
                'tags': {'type': 'keyword'},
                'post_count': {'type': 'integer', 'index': False},  # Not indexed
                'followers': {'type': 'integer', 'index': False},  # Not indexed
                'metadata': {'type': 'text', 'index': False}  # Not indexed
            }
        }
    }

def generate_user_document():
    """Generate a single user document with fake data"""
    departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations', 'Support']
    tags = ['python', 'java', 'javascript', 'react', 'docker', 'kubernetes', 'aws', 'azure', 'ml', 'data']
    
    joined_date = fake.date_between(start_date='-5y', end_date='today')
    last_login = fake.date_time_between(start_date=joined_date, end_date='now')
    
    return {
        'user_id': fake.uuid4(),
        'username': fake.user_name(),
        'email': fake.email(),
        'full_name': fake.name(),
        'bio': fake.text(max_nb_chars=200),
        'age': random.randint(18, 70),
        'salary': round(random.uniform(30000, 200000), 2),
        'department': random.choice(departments),
        'job_title': fake.job(),
        'location': {
            'city': fake.city(),
            'country': fake.country(),
            'latitude': float(fake.latitude()),
            'longitude': float(fake.longitude())
        },
        'joined_date': joined_date.isoformat(),
        'last_login': last_login.isoformat(),
        'is_active': random.choice([True, False]),
        'tags': random.sample(tags, k=random.randint(1, 5)),
        'post_count': random.randint(0, 1000),
        'followers': random.randint(0, 10000),
        'metadata': fake.text(max_nb_chars=500)
    }

def bulk_index_documents(index_name, num_docs, batch_size=500):
    """Bulk index documents to Elasticsearch"""
    print(f"Generating and indexing {num_docs} documents to '{index_name}'...")
    
    def generate_actions():
        for i in range(num_docs):
            yield {
                '_index': index_name,
                '_source': generate_user_document()
            }
            
            if (i + 1) % 1000 == 0:
                print(f"  Generated {i + 1} documents...")
    
    start_time = time.time()
    success, failed = helpers.bulk(
        es,
        generate_actions(),
        chunk_size=batch_size,
        request_timeout=30
    )
    elapsed = time.time() - start_time
    
    print(f"Indexed {success} documents in {elapsed:.2f} seconds")
    if failed:
        print(f"Failed to index {len(failed)} documents")
    
    # Refresh the index to make documents searchable immediately
    es.indices.refresh(index=index_name)
    
    return success

def create_index_with_mapping(index_name, mapping):
    """Create an index with the specified mapping"""
    if es.indices.exists(index=index_name):
        print(f"Deleting existing index '{index_name}'...")
        es.indices.delete(index=index_name)
    
    print(f"Creating index '{index_name}'...")
    es.indices.create(index=index_name, body=mapping)
    
    # Verify mapping
    created_mapping = es.indices.get_mapping(index=index_name)
    field_count = len(created_mapping[index_name]['mappings']['properties'])
    print(f"Index created with {field_count} mapped fields")

def main():
    parser = argparse.ArgumentParser(description='Create test data for Elasticsearch query performance testing')
    parser.add_argument('--docs', type=int, default=10000, help='Number of documents to create (default: 10000)')
    parser.add_argument('--batch-size', type=int, default=500, help='Batch size for bulk indexing (default: 500)')
    parser.add_argument('--create-both', action='store_true', help='Create both indexed and non-indexed indices')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Elasticsearch Data Generation Script")
    print("=" * 60)
    
    # Check Elasticsearch connection
    if not es.ping():
        print("Error: Cannot connect to Elasticsearch at http://localhost:9200")
        print("Please ensure Elasticsearch is running.")
        return
    
    info = es.info()
    print(f"Connected to Elasticsearch {info['version']['number']}")
    print()
    
    if args.create_both:
        # Create both indices for comparison
        print("Creating TWO indices for comparison:")
        print("1. 'users_indexed' - All fields indexed (normal)")
        print("2. 'users_non_indexed' - Some fields not indexed")
        print("-" * 60)
        
        # Create indexed version
        create_index_with_mapping('users_indexed', create_indexed_mapping())
        indexed_count = bulk_index_documents('users_indexed', args.docs, args.batch_size)
        print()
        
        # Create non-indexed version
        create_index_with_mapping('users_non_indexed', create_non_indexed_mapping())
        non_indexed_count = bulk_index_documents('users_non_indexed', args.docs, args.batch_size)
        print()
        
        print("=" * 60)
        print("Data generation complete!")
        print(f"- users_indexed: {indexed_count} documents")
        print(f"- users_non_indexed: {non_indexed_count} documents")
        print("\nNon-indexed fields in 'users_non_indexed':")
        print("  - email, bio, salary, job_title")
        print("  - location.country, location.latitude, location.longitude")
        print("  - last_login, post_count, followers, metadata")
        print("\nYou can now run query performance tests to compare the indices.")
        
    else:
        # Create only the indexed version
        print("Creating index 'users_indexed' with all fields indexed...")
        print("-" * 60)
        
        create_index_with_mapping('users_indexed', create_indexed_mapping())
        count = bulk_index_documents('users_indexed', args.docs, args.batch_size)
        
        print("=" * 60)
        print(f"Data generation complete! Created {count} documents in 'users_indexed'")
        print("\nTo create both indexed and non-indexed versions for comparison,")
        print("run with --create-both flag:")
        print("  python create_data.py --create-both")

if __name__ == '__main__':
    main()
