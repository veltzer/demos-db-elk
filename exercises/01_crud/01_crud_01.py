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
    except:
        print(response.text)
