#!/bin/env python

from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import random
import math

es = Elasticsearch(["http://localhost:9200"])

# Delete and create index
if es.indices.exists(index="products"):
    es.indices.delete(index="products")

mapping = {
    "mappings": {
        "properties": {
            "name": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}}
            },
            "description": {"type": "text"},
            "category": {"type": "keyword"},
            "brand": {"type": "keyword"},
            "price": {"type": "float"},
            "original_price": {"type": "float"},
            "rating": {"type": "float"},
            "review_count": {"type": "integer"},
            "sales_count": {"type": "integer"},
            "view_count": {"type": "integer"},
            "stock_quantity": {"type": "integer"},
            "is_featured": {"type": "boolean"},
            "is_on_sale": {"type": "boolean"},
            "created_date": {"type": "date"},
            "last_restocked": {"type": "date"},
            "tags": {"type": "keyword"},
            "location": {"type": "geo_point"},
            "profit_margin": {"type": "float"}
        }
    }
}

es.indices.create(index="products", body=mapping)

# Generate sample products
products = []
categories = ["Electronics", "Clothing", "Books", "Home & Garden", "Sports"]
brands = ["TechPro", "StyleMax", "BookWorld", "HomePlus", "SportGear"]

for i in range(1, 101):
    price = round(random.uniform(10, 500), 2)
    original_price = price * random.uniform(1.0, 1.5)
    created_days_ago = random.randint(1, 365)

    product = {
        "name": f"Product {i} - {random.choice(['Premium', 'Standard', 'Basic', 'Pro', 'Plus'])}",
        "description": f"High quality product with excellent features and great value. Model {i}",
        "category": random.choice(categories),
        "brand": random.choice(brands),
        "price": price,
        "original_price": round(original_price, 2),
        "rating": round(random.uniform(3.0, 5.0), 1),
        "review_count": random.randint(0, 500),
        "sales_count": random.randint(0, 1000),
        "view_count": random.randint(100, 10000),
        "stock_quantity": random.randint(0, 100),
        "is_featured": random.choice([True, False]),
        "is_on_sale": price < original_price,
        "created_date": (datetime.now() - timedelta(days=created_days_ago)).isoformat(),
        "last_restocked": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
        "tags": random.sample(["bestseller", "new", "trending", "clearance", "exclusive"], k=random.randint(0, 3)),
        "location": {
            "lat": 40.7128 + random.uniform(-1, 1),
            "lon": -74.0060 + random.uniform(-1, 1)
        },
        "profit_margin": round(random.uniform(0.1, 0.5), 2)
    }
    products.append(product)
    es.index(index="products", id=i, body=product)

es.indices.refresh(index="products")
print(f"Indexed {len(products)} products")
