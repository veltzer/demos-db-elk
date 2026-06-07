#!/usr/bin/env python
from elasticsearch import Elasticsearch

# Initialize client
es = Elasticsearch(
    ['http://localhost:9200'],
    basic_auth=('elastic', 'your-password'),
    verify_certs=False,
)

INDEX_NAME = "products"

# Check existing mappings
es.indices.get_mapping(index=INDEX_NAME)

# Reindex to new index with correct mappings if needed
