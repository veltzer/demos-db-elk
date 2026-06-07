#!/usr/bin/env python
from elasticsearch import Elasticsearch

# Initialize client
es = Elasticsearch(
    ['http://localhost:9200'],
    basic_auth=('elastic', 'your-password'),
    verify_certs=False,
)

INDEX_NAME = "products"


def mget_documents():
    """Get multiple documents in one request"""
    doc_ids = ["1", "2", "3"]
    response = es.mget(
        index=INDEX_NAME,
        body={"ids": doc_ids}
    )
    
    print("Multiple Get Results:")
    for doc in response['docs']:
        if doc['found']:
            print(f"- {doc['_id']}: {doc['_source']['name']}")
        else:
            print(f"- {doc['_id']}: Not found")
    
    return response

def count_documents():
    """Count documents matching a query"""
    # Count all documents
    total = es.count(index=INDEX_NAME)['count']
    print(f"Total documents: {total}")
    
    # Count with query
    query = {"query": {"term": {"category": "Electronics"}}}
    electronics_count = es.count(index=INDEX_NAME, body=query)['count']
    print(f"Electronics products: {electronics_count}")
    
    return total, electronics_count

def scroll_through_results():
    """Use scroll API for large result sets"""
    # Initial search with scroll
    response = es.search(
        index=INDEX_NAME,
        scroll='2m',  # Keep scroll context for 2 minutes
        size=2,  # Get 2 documents per batch
        body={"query": {"match_all": {}}}
    )
    
    scroll_id = response['_scroll_id']
    results = response['hits']['hits']
    
    print("Scrolling through results (batch size: 2)")
    batch = 1
    
    while results:
        print(f"\nBatch {batch}:")
        for hit in results:
            print(f"- {hit['_source']['name']}")
        
        # Get next batch
        response = es.scroll(scroll_id=scroll_id, scroll='2m')
        scroll_id = response['_scroll_id']
        results = response['hits']['hits']
        batch += 1
    
    # Clear scroll context
    es.clear_scroll(scroll_id=scroll_id)
    print("\nScroll context cleared")

def reindex_documents():
    """Reindex documents to a new index"""
    new_index = f"{INDEX_NAME}_v2"
    
    # Create new index with updated mappings
    es.indices.create(
        index=new_index,
        body={
            "mappings": {
                "properties": {
                    "product_id": {"type": "keyword"},
                    "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "category": {"type": "keyword"},
                    "price": {"type": "float"},
                    "stock_quantity": {"type": "integer"},
                    "description": {"type": "text"},
                    "tags": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "in_stock": {"type": "boolean"},
                    "last_updated": {"type": "date"}
                }
            }
        }
    )
    
    # Reindex
    response = es.reindex(
        body={
            "source": {"index": INDEX_NAME},
            "dest": {"index": new_index}
        }
    )
    
    print(f"Reindexed {response['total']} documents to {new_index}")
    
    # Clean up - delete new index
    es.indices.delete(index=new_index)
    print(f"Cleaned up {new_index}")
    
    return response

# Execute advanced operations
mget_documents()
count_documents()
scroll_through_results()
reindex_documents()
