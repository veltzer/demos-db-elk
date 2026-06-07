#!/usr/bin/env python
"""
Elasticsearch CRUD operations using requests library
"""

import requests
import json

# Configuration
ES_HOST = "localhost"
ES_PORT = 9200
ES_USER = "elastic"
ES_PASSWORD = "your-password"
ES_URL = f"http://{ES_HOST}:{ES_PORT}"
INDEX_NAME = "products"

# Session with authentication
session = requests.Session()
session.auth = (ES_USER, ES_PASSWORD)
session.headers.update({'Content-Type': 'application/json'})


def pretty_print(response):
    """Pretty print JSON response"""
    try:
        print(json.dumps(response.json(), indent=2))
    except ValueError:
        print(response.text)


def delete_document(doc_id: str):
    """Delete a single document"""
    response = session.delete(f"{ES_URL}/{INDEX_NAME}/_doc/{doc_id}")
    print(f"Delete document status: {response.status_code}")
    pretty_print(response)
    return response

def delete_by_query():
    """Delete documents by query"""
    delete_query = {
        "query": {
            "term": {"in_stock": False}
        }
    }
    
    response = session.post(
        f"{ES_URL}/{INDEX_NAME}/_delete_by_query",
        data=json.dumps(delete_query)
    )
    
    print(f"Delete by query status: {response.status_code}")
    pretty_print(response)
    return response

def delete_index():
    """Delete entire index"""
    response = session.delete(f"{ES_URL}/{INDEX_NAME}")
    print(f"Delete index status: {response.status_code}")
    pretty_print(response)
    return response

# Execute
delete_document("1")
delete_by_query()
# delete_index()  # Uncomment to delete entire index
