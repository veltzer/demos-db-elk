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
        }
    }
    
    response = session.put(
        f"{ES_URL}/{INDEX_NAME}",
        data=json.dumps(mappings)
    )
    
    print(f"Index creation status: {response.status_code}")
    pretty_print(response)
    return response

# Execute
create_index()
