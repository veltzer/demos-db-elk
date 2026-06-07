#!/usr/bin/env python
import json

from elasticsearch import Elasticsearch

# Initialize client
es = Elasticsearch(
    ['http://localhost:9200'],
)

INDEX_NAME = "products"


def get_document(doc_id: str):
    """Get a specific document by ID"""
    try:
        response = es.get(index=INDEX_NAME, id=doc_id)
        print(f"Document ID {doc_id}:")
        print(json.dumps(response['_source'], indent=2))
        return response
    except Exception as e:
        print(f"Error getting document: {e}")
        return None

def search_all_documents():
    """Search all documents"""
    response = es.search(
        index=INDEX_NAME,
        body={
            "query": {"match_all": {}},
            "size": 100
        }
    )
    
    print(f"Total hits: {response['hits']['total']['value']}")
    for hit in response['hits']['hits']:
        print(f"\nID: {hit['_id']}, Score: {hit['_score']}")
        print(f"Product: {hit['_source']['name']} - ${hit['_source']['price']}")
    
    return response

def search_with_query():
    """Search with specific query"""
    # Search for electronics under $200
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"category": "Electronics"}},
                    {"range": {"price": {"lte": 200}}}
                ],
                "filter": [
                    {"term": {"in_stock": True}}
                ]
            }
        },
        "sort": [
            {"price": {"order": "asc"}}
        ],
        "size": 5
    }
    
    response = es.search(index=INDEX_NAME, body=query)
    
    print("Electronics under $200 (in stock):")
    for hit in response['hits']['hits']:
        source = hit['_source']
        print(f"- {source['name']}: ${source['price']}")
    
    return response

def search_with_aggregations():
    """Search with aggregations"""
    query = {
        "size": 0,  # Don't return documents, only aggregations
        "aggs": {
            "categories": {
                "terms": {
                    "field": "category",
                    "size": 10
                },
                "aggs": {
                    "avg_price": {
                        "avg": {"field": "price"}
                    },
                    "total_stock": {
                        "sum": {"field": "stock_quantity"}
                    }
                }
            },
            "price_ranges": {
                "range": {
                    "field": "price",
                    "ranges": [
                        {"key": "budget", "to": 50},
                        {"key": "mid-range", "from": 50, "to": 150},
                        {"key": "premium", "from": 150}
                    ]
                }
            },
            "in_stock_stats": {
                "filter": {"term": {"in_stock": True}},
                "aggs": {
                    "total_value": {
                        "sum": {
                            "script": {
                                "source": "doc['price'].value * doc['stock_quantity'].value"
                            }
                        }
                    }
                }
            }
        }
    }
    
    response = es.search(index=INDEX_NAME, body=query)
    
    print("\n=== Aggregation Results ===")
    
    # Category statistics
    print("\nCategory Statistics:")
    for bucket in response['aggregations']['categories']['buckets']:
        print(f"- {bucket['key']}:")
        print(f"  Count: {bucket['doc_count']}")
        print(f"  Avg Price: ${bucket['avg_price']['value']:.2f}")
        print(f"  Total Stock: {bucket['total_stock']['value']}")
    
    # Price ranges
    print("\nPrice Ranges:")
    for bucket in response['aggregations']['price_ranges']['buckets']:
        print(f"- {bucket['key']}: {bucket['doc_count']} products")
    
    # Stock value
    total_value = response['aggregations']['in_stock_stats']['total_value']['value']
    print(f"\nTotal inventory value (in stock): ${total_value:.2f}")
    
    return response

def search_with_highlighting():
    """Search with text highlighting"""
    query = {
        "query": {
            "multi_match": {
                "query": "wireless headphones",
                "fields": ["name", "description", "tags"]
            }
        },
        "highlight": {
            "fields": {
                "name": {},
                "description": {},
                "tags": {}
            },
            "pre_tags": ["<mark>"],
            "post_tags": ["</mark>"]
        }
    }
    
    response = es.search(index=INDEX_NAME, body=query)
    
    print("\nSearch results with highlighting:")
    for hit in response['hits']['hits']:
        print(f"\nProduct: {hit['_source']['name']}")
        if 'highlight' in hit:
            for field, highlights in hit['highlight'].items():
                print(f"  {field}: {highlights[0]}")
    
    return response

# Execute
get_document("1")
search_all_documents()
search_with_query()
search_with_aggregations()
search_with_highlighting()
