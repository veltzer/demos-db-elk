#!/usr/bin/env python
"""
Elasticsearch CRUD operations using requests library
"""

import requests
import json
from datetime import datetime
from typing import Optional

# Configuration
ES_HOST = "localhost"
ES_PORT = 9200
ES_URL = f"http://{ES_HOST}:{ES_PORT}"
INDEX_NAME = "products"

# HTTP session (security disabled: no authentication)
session = requests.Session()
session.headers.update({'Content-Type': 'application/json'})


def pretty_print(response):
    """Pretty print JSON response"""
    try:
        print(json.dumps(response.json(), indent=2))
    except ValueError:
        print(response.text)


def insert_single_document(doc_id: Optional[str] = None):
    """Insert a single document"""
    document = {
        "product_id": "PROD001",
        "name": "Wireless Bluetooth Headphones",
        "category": "Electronics",
        "price": 79.99,
        "stock_quantity": 150,
        "description": "High-quality wireless headphones with noise cancellation",
        "tags": ["wireless", "bluetooth", "audio"],
        "created_at": datetime.now().isoformat(),
        "in_stock": True
    }
    
    if doc_id:
        # Insert with specific ID
        url = f"{ES_URL}/{INDEX_NAME}/_doc/{doc_id}"
        response = session.put(url, data=json.dumps(document))
    else:
        # Insert with auto-generated ID
        url = f"{ES_URL}/{INDEX_NAME}/_doc"
        response = session.post(url, data=json.dumps(document))
    
    print(f"Insert status: {response.status_code}")
    pretty_print(response)
    return response

def bulk_insert_documents():
    """Bulk insert multiple documents"""
    products = [
        {
            "product_id": "PROD002",
            "name": "Smart Watch Pro",
            "category": "Electronics",
            "price": 299.99,
            "stock_quantity": 75,
            "description": "Advanced fitness tracking",
            "tags": ["smartwatch", "fitness"],
            "created_at": datetime.now().isoformat(),
            "in_stock": True
        },
        {
            "product_id": "PROD003",
            "name": "Yoga Mat Premium",
            "category": "Sports",
            "price": 34.99,
            "stock_quantity": 200,
            "description": "Non-slip exercise mat",
            "tags": ["yoga", "fitness"],
            "created_at": datetime.now().isoformat(),
            "in_stock": True
        },
        {
            "product_id": "PROD004",
            "name": "Coffee Maker Deluxe",
            "category": "Appliances",
            "price": 129.99,
            "stock_quantity": 50,
            "description": "Programmable coffee maker",
            "tags": ["coffee", "kitchen"],
            "created_at": datetime.now().isoformat(),
            "in_stock": True
        }
    ]
    
    # Build bulk request body
    bulk_data = []
    for i, product in enumerate(products, start=2):
        bulk_data.append(json.dumps({"index": {"_id": str(i)}}))
        bulk_data.append(json.dumps(product))
    
    # Join with newlines (NDJSON format)
    bulk_body = '\n'.join(bulk_data) + '\n'
    
    # Send bulk request
    response = session.post(
        f"{ES_URL}/{INDEX_NAME}/_bulk",
        data=bulk_body,
        headers={'Content-Type': 'application/x-ndjson'}
    )
    
    print(f"Bulk insert status: {response.status_code}")
    result = response.json()
    print(f"Errors: {result.get('errors', False)}")
    print(f"Items processed: {len(result.get('items', []))}")
    return response

# Execute
insert_single_document("1")
bulk_insert_documents()
