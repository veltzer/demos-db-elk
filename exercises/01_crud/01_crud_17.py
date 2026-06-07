#!/usr/bin/env python
from elasticsearch import Elasticsearch

# Initialize client
es = Elasticsearch(
    ['http://localhost:9200'],
)

INDEX_NAME = "products"

doc = {"name": "example"}

# Force refresh after insert
es.index(index=INDEX_NAME, id="1", document=doc, refresh=True)

# Or refresh the entire index
es.indices.refresh(index=INDEX_NAME)
