#!/usr/bin/env python
def update_document_full(doc_id: str):
    """Full document update (replace)"""
    updated_doc = {
        "product_id": "PROD001",
        "name": "Wireless Bluetooth Headphones - Premium",
        "category": "Electronics",
        "price": 99.99,
        "stock_quantity": 175,
        "description": "Premium wireless headphones with ANC",
        "tags": ["wireless", "bluetooth", "audio", "premium"],
        "created_at": datetime.now().isoformat(),
        "in_stock": True
    }
    
    response = session.put(
        f"{ES_URL}/{INDEX_NAME}/_doc/{doc_id}",
        data=json.dumps(updated_doc)
    )
    
    print(f"Full update status: {response.status_code}")
    pretty_print(response)
    return response

def update_document_partial(doc_id: str):
    """Partial document update"""
    update_data = {
        "doc": {
            "price": 89.99,
            "stock_quantity": 200,
            "tags": ["wireless", "bluetooth", "audio", "sale"]
        }
    }
    
    response = session.post(
        f"{ES_URL}/{INDEX_NAME}/_update/{doc_id}",
        data=json.dumps(update_data)
    )
    
    print(f"Partial update status: {response.status_code}")
    pretty_print(response)
    return response

def update_by_query():
    """Update multiple documents by query"""
    update_query = {
        "query": {
            "term": {"category": "Electronics"}
        },
        "script": {
            "source": "ctx._source.price *= params.discount",
            "params": {"discount": 0.9}  # 10% discount
        }
    }
    
    response = session.post(
        f"{ES_URL}/{INDEX_NAME}/_update_by_query",
        data=json.dumps(update_query)
    )
    
    print(f"Update by query status: {response.status_code}")
    pretty_print(response)
    return response

# Execute
update_document_full("1")
update_document_partial("1")
update_by_query()
