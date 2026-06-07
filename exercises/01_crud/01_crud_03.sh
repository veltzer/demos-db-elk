#!/bin/bash -eu
# Insert with auto-generated ID
curl -X POST "localhost:9200/products/_doc" \
  -H 'Content-Type: application/json' \
  -d '{
    "product_id": "PROD001",
    "name": "Wireless Bluetooth Headphones",
    "category": "Electronics",
    "price": 79.99,
    "stock_quantity": 150,
    "description": "High-quality wireless headphones with noise cancellation",
    "tags": ["wireless", "bluetooth", "audio"],
    "created_at": "2024-01-15T10:30:00Z",
    "in_stock": true
  }'

# Insert with specific ID
curl -X PUT "localhost:9200/products/_doc/1" \
  -H 'Content-Type: application/json' \
  -d '{
    "product_id": "PROD002",
    "name": "Smart Watch Pro",
    "category": "Electronics",
    "price": 299.99,
    "stock_quantity": 75,
    "description": "Advanced fitness tracking and health monitoring",
    "tags": ["smartwatch", "fitness", "health"],
    "created_at": "2024-01-16T14:20:00Z",
    "in_stock": true
  }'
