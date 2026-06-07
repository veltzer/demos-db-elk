#!/bin/bash -eu
curl -X POST "localhost:9200/orders/_doc/1?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Alice", "product": "Laptop", "category": "Electronics", "price": 999.99, "quantity": 1, "date": "2024-01-15", "status": "shipped" }'

curl -X POST "localhost:9200/orders/_doc/2?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Bob", "product": "Coffee Mug", "category": "Kitchen", "price": 12.50, "quantity": 2, "date": "2024-01-16", "status": "delivered" }'

curl -X POST "localhost:9200/orders/_doc/3?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Alice", "product": "Wireless Mouse", "category": "Electronics", "price": 25.99, "quantity": 1, "date": "2024-01-17", "status": "delivered" }'

curl -X POST "localhost:9200/orders/_doc/4?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Charlie", "product": "Running Shoes", "category": "Sports", "price": 89.99, "quantity": 1, "date": "2024-01-18", "status": "pending" }'

curl -X POST "localhost:9200/orders/_doc/5?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Bob", "product": "Yoga Mat", "category": "Sports", "price": 35.00, "quantity": 1, "date": "2024-01-19", "status": "shipped" }'

curl -X POST "localhost:9200/orders/_doc/6?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Alice", "product": "Smartphone", "category": "Electronics", "price": 599.99, "quantity": 1, "date": "2024-01-20", "status": "delivered" }'

curl -X POST "localhost:9200/orders/_doc/7?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Diana", "product": "Cooking Pan", "category": "Kitchen", "price": 45.99, "quantity": 1, "date": "2024-01-21", "status": "shipped" }'

curl -X POST "localhost:9200/orders/_doc/8?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Charlie", "product": "Headphones", "category": "Electronics", "price": 150.00, "quantity": 1, "date": "2024-01-22", "status": "delivered" }'

curl -X POST "localhost:9200/orders/_doc/9?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Bob", "product": "Water Bottle", "category": "Sports", "price": 18.99, "quantity": 3, "date": "2024-01-23", "status": "pending" }'

curl -X POST "localhost:9200/orders/_doc/10?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Diana", "product": "Blender", "category": "Kitchen", "price": 79.99, "quantity": 1, "date": "2024-01-24", "status": "delivered" }'
