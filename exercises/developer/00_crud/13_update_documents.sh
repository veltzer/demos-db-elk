#!/bin/bash -eu
# Full update
curl -X PUT "localhost:9200/products/_doc/1" \
  -H 'Content-Type: application/json' \
  -d '{
    "product_id": "PROD002",
    "name": "Smart Watch Pro - Updated",
    "category": "Electronics",
    "price": 249.99,
    "stock_quantity": 100,
    "description": "Advanced fitness tracking - Now with GPS",
    "tags": ["smartwatch", "fitness", "health", "gps"],
    "created_at": "2024-01-16T14:20:00Z",
    "in_stock": true
  }'

# Partial update
curl -X POST "localhost:9200/products/_update/1" \
  -H 'Content-Type: application/json' \
  -d '{
    "doc": {
      "price": 229.99,
      "stock_quantity": 120
    }
  }'

# Update with script
curl -X POST "localhost:9200/products/_update/1" \
  -H 'Content-Type: application/json' \
  -d '{
    "script": {
      "source": "ctx._source.stock_quantity += params.count",
      "params": {
        "count": 10
      }
    }
  }'
