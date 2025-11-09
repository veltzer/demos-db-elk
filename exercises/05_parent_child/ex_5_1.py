#!/bin/env python

from elasticsearch import Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Create an e-commerce scenario with products and reviews
if es.indices.exists(index="ecommerce"):
    es.indices.delete(index="ecommerce")

ecommerce_mapping = {
    "mappings": {
        "properties": {
            "join_field": {
                "type": "join",
                "relations": {
                    "product": "review"
                }
            },
            "name": {"type": "text"},
            "description": {"type": "text"},
            "category": {"type": "keyword"},
            "price": {"type": "float"},
            "rating": {"type": "float"},
            "review_text": {"type": "text"},
            "reviewer": {"type": "keyword"},
            "verified_purchase": {"type": "boolean"},
            "helpful_votes": {"type": "integer"},
            "created_at": {"type": "date"}
        }
    }
}

es.indices.create(index="ecommerce", body=ecommerce_mapping)

# Index products
products = [
    {
        "name": "Wireless Headphones Pro",
        "description": "Premium noise-cancelling wireless headphones",
        "category": "Electronics",
        "price": 299.99,
        "join_field": "product"
    },
    {
        "name": "Smart Watch Ultra",
        "description": "Advanced fitness and health tracking smartwatch",
        "category": "Electronics",
        "price": 399.99,
        "join_field": "product"
    }
]

for i, product in enumerate(products, 1):
    es.index(index="ecommerce", id=f"product_{i}", body=product)

# Index reviews
reviews = [
    {
        "rating": 5,
        "review_text": "Amazing sound quality and comfort!",
        "reviewer": "john_doe",
        "verified_purchase": True,
        "helpful_votes": 45,
        "created_at": "2024-01-10",
        "join_field": {"name": "review", "parent": "product_1"}
    },
    {
        "rating": 4,
        "review_text": "Good but battery could be better",
        "reviewer": "jane_smith",
        "verified_purchase": True,
        "helpful_votes": 23,
        "created_at": "2024-01-15",
        "join_field": {"name": "review", "parent": "product_1"}
    }
]

for i, review in enumerate(reviews, 1):
    parent_id = review["join_field"]["parent"]
    es.index(index="ecommerce", id=f"review_{i}", body=review, routing=parent_id)

es.indices.refresh(index="ecommerce")

# Query: Find products with average rating above 4
avg_rating_query = {
    "query": {
        "has_child": {
            "type": "review",
            "query": {"match_all": {}},
            "inner_hits": {
                "size": 0,
                "_source": False
            }
        }
    },
    "aggs": {
        "products": {
            "terms": {
                "field": "name.keyword",
                "size": 10
            },
            "aggs": {
                "avg_rating": {
                    "children": {
                        "type": "review"
                    },
                    "aggs": {
                        "rating": {
                            "avg": {
                                "field": "rating"
                            }
                        }
                    }
                }
            }
        }
    }
}

# Note: This is a simplified example. In practice, you'd need more complex aggregations
print("Products with reviews (example query created)")
