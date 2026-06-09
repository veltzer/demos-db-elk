#!/usr/bin/env python
from datetime import datetime

from elasticsearch import Elasticsearch

# Initialize client
es = Elasticsearch(
    ['http://localhost:9200'],
)

INDEX_NAME = "products"


def update_document_full(doc_id: str):
    """Full document update (replace)"""
    updated_doc = {
        "product_id": "PROD001",
        "name": "Wireless Bluetooth Headphones - Premium Edition",
        "category": "Electronics",
        "price": 119.99,
        "stock_quantity": 100,
        "description": "Premium wireless headphones with advanced ANC technology",
        "tags": ["wireless", "bluetooth", "audio", "premium", "anc"],
        "created_at": datetime.now(),
        "in_stock": True,
        "last_updated": datetime.now()
    }
    
    response = es.index(index=INDEX_NAME, id=doc_id, document=updated_doc)
    print(f"Full update result: {response['result']}")
    return response

def update_document_partial(doc_id: str):
    """Partial document update"""
    update_body = {
        "doc": {
            "price": 109.99,
            "stock_quantity": 85,
            "last_updated": datetime.now()
        }
    }
    
    response = es.update(index=INDEX_NAME, id=doc_id, body=update_body)
    print(f"Partial update result: {response['result']}")
    return response

def update_with_script(doc_id: str):
    """Update using script"""
    script_body = {
        "script": {
            "source": """
                ctx._source.stock_quantity += params.quantity;
                ctx._source.last_updated = params.now;
                if (ctx._source.stock_quantity <= 0) {
                    ctx._source.in_stock = false;
                } else {
                    ctx._source.in_stock = true;
                }
            """,
            "params": {
                "quantity": -10,  # Reduce stock by 10
                "now": datetime.now().isoformat()
            }
        }
    }
    
    response = es.update(index=INDEX_NAME, id=doc_id, body=script_body)
    print(f"Script update result: {response['result']}")
    return response

def update_by_query():
    """Update multiple documents by query"""
    # Apply 15% discount to all Electronics
    update_query = {
        "script": {
            "source": """
                ctx._source.price = ctx._source.price * params.discount;
                ctx._source.tags.add(params.tag);
                ctx._source.last_updated = params.now;
            """,
            "params": {
                "discount": 0.85,
                "tag": "sale",
                "now": datetime.now().isoformat()
            }
        },
        "query": {
            "term": {"category": "Electronics"}
        }
    }
    
    response = es.update_by_query(index=INDEX_NAME, body=update_query)
    print(f"Update by query - Updated: {response['updated']}, Failed: {response['failures']}")
    return response

def upsert_document():
    """Upsert - Update if exists, insert if not"""
    doc_id = "99"
    upsert_body = {
        "doc": {
            "price": 159.99,
            "stock_quantity": 25,
            "last_updated": datetime.now()
        },
        "upsert": {
            "product_id": "PROD099",
            "name": "New Product via Upsert",
            "category": "Electronics",
            "price": 159.99,
            "stock_quantity": 25,
            "description": "Created via upsert operation",
            "tags": ["new", "upsert"],
            "created_at": datetime.now(),
            "in_stock": True
        }
    }
    
    response = es.update(index=INDEX_NAME, id=doc_id, body=upsert_body)
    print(f"Upsert result: {response['result']} (version: {response['_version']})")
    return response

# Execute
update_document_full("1")
update_document_partial("1")
update_with_script("1")
update_by_query()
upsert_document()
