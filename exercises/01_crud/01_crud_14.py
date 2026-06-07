#!/usr/bin/env python
"""
Complete Elasticsearch CRUD example
Run this script to see all operations in action
"""

from elasticsearch import Elasticsearch

# Initialize connection
es = Elasticsearch(
    ['http://localhost:9200'],
    basic_auth=('elastic', 'your-password'),
    verify_certs=False
)

INDEX_NAME = "products_demo"

def run_complete_demo():
    """Run complete CRUD demonstration"""
    
    print("=" * 50)
    print("ELASTICSEARCH CRUD OPERATIONS DEMO")
    print("=" * 50)
    
    # 1. CREATE INDEX
    print("\n1. CREATING INDEX")
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
    
    es.indices.create(
        index=INDEX_NAME,
        body={
            "mappings": {
                "properties": {
                    "name": {"type": "text"},
                    "price": {"type": "float"},
                    "category": {"type": "keyword"},
                    "in_stock": {"type": "boolean"}
                }
            }
        }
    )
    print(f"✓ Index '{INDEX_NAME}' created")
    
    # 2. INSERT DOCUMENTS
    print("\n2. INSERTING DOCUMENTS")
    products = [
        {"name": "Laptop", "price": 999.99, "category": "Electronics", "in_stock": True},
        {"name": "Mouse", "price": 29.99, "category": "Electronics", "in_stock": True},
        {"name": "Keyboard", "price": 79.99, "category": "Electronics", "in_stock": False},
        {"name": "Monitor", "price": 299.99, "category": "Electronics", "in_stock": True},
        {"name": "Desk Chair", "price": 199.99, "category": "Furniture", "in_stock": True}
    ]
    
    for i, product in enumerate(products, 1):
        es.index(index=INDEX_NAME, id=str(i), document=product)
        print(f"✓ Inserted: {product['name']}")
    
    # Refresh index to make documents searchable immediately
    es.indices.refresh(index=INDEX_NAME)
    
    # 3. READ/SEARCH DOCUMENTS
    print("\n3. SEARCHING DOCUMENTS")
    
    # Get specific document
    doc = es.get(index=INDEX_NAME, id="1")
    print(f"✓ Retrieved doc 1: {doc['_source']['name']}")
    
    # Search all
    results = es.search(index=INDEX_NAME, body={"query": {"match_all": {}}})
    print(f"✓ Total documents: {results['hits']['total']['value']}")
    
    # Search with filter
    results = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "bool": {
                    "must": [{"term": {"category": "Electronics"}}],
                    "filter": [{"term": {"in_stock": True}}]
                }
            }
        }
    )
    print(f"✓ Electronics in stock: {results['hits']['total']['value']}")
    
    # 4. UPDATE DOCUMENTS
    print("\n4. UPDATING DOCUMENTS")
    
    # Update price
    es.update(
        index=INDEX_NAME,
        id="1",
        body={"doc": {"price": 899.99}}
    )
    print("✓ Updated Laptop price to $899.99")
    
    # Update by query - add discount
    es.update_by_query(
        index=INDEX_NAME,
        body={
            "query": {"term": {"category": "Electronics"}},
            "script": {"source": "ctx._source.price *= 0.9"}
        }
    )
    print("✓ Applied 10% discount to all Electronics")
    
    # 5. DELETE DOCUMENTS
    print("\n5. DELETING DOCUMENTS")
    
    # Delete single document
    es.delete(index=INDEX_NAME, id="5")
    print("✓ Deleted document 5 (Desk Chair)")
    
    # Delete by query
    es.delete_by_query(
        index=INDEX_NAME,
        body={"query": {"term": {"in_stock": False}}}
    )
    print("✓ Deleted all out-of-stock items")
    
    # 6. FINAL COUNT
    print("\n6. FINAL STATUS")
    es.indices.refresh(index=INDEX_NAME)
    count = es.count(index=INDEX_NAME)['count']
    print(f"✓ Remaining documents: {count}")
    
    # 7. CLEANUP
    print("\n7. CLEANUP")
    es.indices.delete(index=INDEX_NAME)
    print(f"✓ Index '{INDEX_NAME}' deleted")
    
    print("\n" + "=" * 50)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 50)

if __name__ == "__main__":
    run_complete_demo()
