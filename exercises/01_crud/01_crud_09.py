#!/usr/bin/env python
from datetime import datetime

from elasticsearch import Elasticsearch, helpers

# Initialize client
es = Elasticsearch(
    ['http://localhost:9200'],
    basic_auth=('elastic', 'your-password'),
    verify_certs=False,
)

INDEX_NAME = "products"


def insert_single_document():
    """Insert a single document"""
    document = {
        "product_id": "PROD001",
        "name": "Wireless Bluetooth Headphones",
        "category": "Electronics",
        "price": 79.99,
        "stock_quantity": 150,
        "description": "High-quality wireless headphones with noise cancellation",
        "tags": ["wireless", "bluetooth", "audio"],
        "created_at": datetime.now(),
        "in_stock": True
    }
    
    # Insert with auto-generated ID
    response = es.index(index=INDEX_NAME, document=document)
    print(f"Document inserted (auto ID): {response['_id']}")
    
    # Insert with specific ID
    response = es.index(index=INDEX_NAME, id="1", document=document)
    print(f"Document inserted (ID=1): {response['result']}")
    
    return response

def bulk_insert_documents():
    """Bulk insert multiple documents using helpers"""
    products = [
        {
            "_index": INDEX_NAME,
            "_id": "2",
            "_source": {
                "product_id": "PROD002",
                "name": "Smart Watch Pro",
                "category": "Electronics",
                "price": 299.99,
                "stock_quantity": 75,
                "description": "Advanced fitness tracking",
                "tags": ["smartwatch", "fitness"],
                "created_at": datetime.now(),
                "in_stock": True
            }
        },
        {
            "_index": INDEX_NAME,
            "_id": "3",
            "_source": {
                "product_id": "PROD003",
                "name": "Yoga Mat Premium",
                "category": "Sports",
                "price": 34.99,
                "stock_quantity": 200,
                "description": "Non-slip exercise mat",
                "tags": ["yoga", "fitness"],
                "created_at": datetime.now(),
                "in_stock": True
            }
        },
        {
            "_index": INDEX_NAME,
            "_id": "4",
            "_source": {
                "product_id": "PROD004",
                "name": "Coffee Maker Deluxe",
                "category": "Appliances",
                "price": 129.99,
                "stock_quantity": 50,
                "description": "Programmable coffee maker",
                "tags": ["coffee", "kitchen"],
                "created_at": datetime.now(),
                "in_stock": True
            }
        },
        {
            "_index": INDEX_NAME,
            "_id": "5",
            "_source": {
                "product_id": "PROD005",
                "name": "Running Shoes",
                "category": "Sports",
                "price": 89.99,
                "stock_quantity": 0,
                "description": "Professional running shoes",
                "tags": ["running", "sports"],
                "created_at": datetime.now(),
                "in_stock": False
            }
        }
    ]
    
    # Use helpers for efficient bulk operations
    success, failed = helpers.bulk(es, products, stats_only=True)
    print(f"Bulk insert - Success: {success}, Failed: {failed}")
    
    return success, failed

def bulk_insert_generator():
    """Bulk insert using generator (memory efficient for large datasets)"""
    def generate_products():
        for i in range(6, 11):
            yield {
                "_index": INDEX_NAME,
                "_id": str(i),
                "_source": {
                    "product_id": f"PROD{i:03d}",
                    "name": f"Product {i}",
                    "category": "General",
                    "price": 50.00 + (i * 10),
                    "stock_quantity": i * 10,
                    "description": f"Description for product {i}",
                    "tags": ["general"],
                    "created_at": datetime.now(),
                    "in_stock": True
                }
            }
    
    success, failed = helpers.bulk(es, generate_products(), stats_only=True)
    print(f"Bulk generator insert - Success: {success}, Failed: {failed}")
    return success, failed

# Execute
insert_single_document()
bulk_insert_documents()
bulk_insert_generator()
