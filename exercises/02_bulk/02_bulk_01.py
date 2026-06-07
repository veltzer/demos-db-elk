#!/usr/bin/env python
"""
Bulk-optimized index setup for Elasticsearch.

Demonstrates the pattern of creating an index with bulk-optimized settings
(no replicas, disabled refresh), then re-enabling normal settings after the
bulk load completes.
"""

import sys
from elasticsearch import Elasticsearch

ES_HOST = "localhost"
ES_PORT = 9200
ES_USER = "elastic"
ES_PASSWORD = "changeme"
INDEX_NAME = "products"

es = Elasticsearch(
    [{"host": ES_HOST, "port": ES_PORT, "scheme": "http"}],
    basic_auth=(ES_USER, ES_PASSWORD),
    verify_certs=False,
    request_timeout=60,
)

if not es.ping():
    print("Error: Could not connect to Elasticsearch")
    sys.exit(1)

print(f"Connected to Elasticsearch at {ES_HOST}:{ES_PORT}")

# 1. Create index with bulk-optimized settings
if es.indices.exists(index=INDEX_NAME):
    es.indices.delete(index=INDEX_NAME)

es.indices.create(
    index=INDEX_NAME,
    body={
        "settings": {
            "number_of_shards": 2,
            "number_of_replicas": 0,
            "refresh_interval": "-1",
        }
    },
)
print(f"Created index '{INDEX_NAME}' with bulk-optimized settings")

# 2. Perform bulk insert
# ... bulk insert operations ...

# 3. Re-enable normal settings after loading
es.indices.put_settings(
    index=INDEX_NAME,
    body={
        "number_of_replicas": 1,
        "refresh_interval": "1s",
    },
)
print(f"Restored normal settings on index '{INDEX_NAME}'")
