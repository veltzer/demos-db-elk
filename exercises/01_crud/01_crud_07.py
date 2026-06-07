#!/usr/bin/env python
"""
Elasticsearch CRUD operations using official elasticsearch-py client
"""

import sys

from elasticsearch import Elasticsearch

# Initialize client
es = Elasticsearch(
    ['http://localhost:9200'],
    basic_auth=('elastic', 'your-password'),
    verify_certs=False,  # Set to True in production with proper certificates
)

# Verify connection
if es.ping():
    print("Connected to Elasticsearch")
    print(es.info())
else:
    print("Could not connect to Elasticsearch")
    sys.exit(1)

INDEX_NAME = "products"
