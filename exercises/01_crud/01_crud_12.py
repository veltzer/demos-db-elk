#!/usr/bin/env python
def delete_document(doc_id: str):
    """Delete a single document"""
    try:
        response = es.delete(index=INDEX_NAME, id=doc_id)
        print(f"Deleted document {doc_id}: {response['result']}")
        return response
    except Exception as e:
        print(f"Error deleting document: {e}")
        return None

def delete_by_query():
    """Delete documents by query"""
    # Delete all out-of-stock items
    delete_query = {
        "query": {
            "term": {"in_stock": False}
        }
    }
    
    response = es.delete_by_query(index=INDEX_NAME, body=delete_query)
    print(f"Delete by query - Deleted: {response['deleted']}, Failed: {response['failures']}")
    return response

def delete_with_refresh():
    """Delete and immediately refresh index"""
    # Delete and refresh to make changes immediately visible
    response = es.delete(index=INDEX_NAME, id="2", refresh=True)
    print(f"Deleted with refresh: {response['result']}")
    return response

def delete_index():
    """Delete entire index"""
    response = es.indices.delete(index=INDEX_NAME)
    print(f"Index {INDEX_NAME} deleted: {response['acknowledged']}")
    return response

# Execute
delete_document("99")
delete_by_query()
# delete_with_refresh()  # Uncomment to test
# delete_index()  # Uncomment to delete entire index
