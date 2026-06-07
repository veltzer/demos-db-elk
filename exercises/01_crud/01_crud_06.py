#!/usr/bin/env python
def delete_document(doc_id: str):
    """Delete a single document"""
    response = session.delete(f"{ES_URL}/{INDEX_NAME}/_doc/{doc_id}")
    print(f"Delete document status: {response.status_code}")
    pretty_print(response)
    return response

def delete_by_query():
    """Delete documents by query"""
    delete_query = {
        "query": {
            "term": {"in_stock": False}
        }
    }
    
    response = session.post(
        f"{ES_URL}/{INDEX_NAME}/_delete_by_query",
        data=json.dumps(delete_query)
    )
    
    print(f"Delete by query status: {response.status_code}")
    pretty_print(response)
    return response

def delete_index():
    """Delete entire index"""
    response = session.delete(f"{ES_URL}/{INDEX_NAME}")
    print(f"Delete index status: {response.status_code}")
    pretty_print(response)
    return response

# Execute
delete_document("1")
delete_by_query()
# delete_index()  # Uncomment to delete entire index
