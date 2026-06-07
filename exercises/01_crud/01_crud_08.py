#!/usr/bin/env python
def create_index():
    """Create products index with mappings"""
    mappings = {
        "mappings": {
            "properties": {
                "product_id": {"type": "keyword"},
                "name": {"type": "text"},
                "category": {"type": "keyword"},
                "price": {"type": "float"},
                "stock_quantity": {"type": "integer"},
                "description": {"type": "text"},
                "tags": {"type": "keyword"},
                "created_at": {"type": "date"},
                "in_stock": {"type": "boolean"}
            }
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }
    
    # Delete index if exists
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print(f"Deleted existing index: {INDEX_NAME}")
    
    # Create index
    response = es.indices.create(index=INDEX_NAME, body=mappings)
    print(f"Index created: {response}")
    return response

# Execute
create_index()
