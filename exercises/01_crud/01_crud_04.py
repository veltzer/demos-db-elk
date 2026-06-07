#!/usr/bin/env python
"""
Elasticsearch CRUD operations using requests library
"""

import requests
import json
from typing import Dict

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


def get_document(doc_id: str):
    """Get a specific document by ID"""
    response = session.get(f"{ES_URL}/{INDEX_NAME}/_doc/{doc_id}")
    print(f"Get document status: {response.status_code}")
    pretty_print(response)
    return response

def search_documents(query: Dict = None):
    """Search documents with optional query"""
    if query is None:
        query = {"query": {"match_all": {}}}
    
    response = session.get(
        f"{ES_URL}/{INDEX_NAME}/_search",
        data=json.dumps(query)
    )
    
    print(f"Search status: {response.status_code}")
    result = response.json()
    
    # Display results
    hits = result.get('hits', {}).get('hits', [])
    print(f"Total hits: {result.get('hits', {}).get('total', {}).get('value', 0)}")
    
    for hit in hits:
        print(f"\nID: {hit['_id']}")
        print(f"Score: {hit['_score']}")
        print(f"Source: {json.dumps(hit['_source'], indent=2)}")
    
    return response

def search_with_criteria():
    """Search with specific criteria"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"category": "Electronics"}},
                    {"range": {"price": {"gte": 50, "lte": 300}}}
                ]
            }
        },
        "sort": [{"price": "asc"}],
        "size": 10
    }
    
    return search_documents(query)

# Execute
get_document("1")
search_documents()
search_with_criteria()
