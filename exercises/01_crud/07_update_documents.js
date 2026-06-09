#!/usr/bin/env node
// Full update (replaces entire document)
PUT /products/_doc/1
{
  "product_id": "PROD002",
  "name": "Smart Watch Pro - Updated",
  "category": "Electronics",
  "price": 249.99,
  "stock_quantity": 100,
  "description": "Advanced fitness tracking - Now with GPS",
  "tags": ["smartwatch", "fitness", "health", "gps"],
  "created_at": "2024-01-16T14:20:00Z",
  "in_stock": true
}

// Partial update
POST /products/_update/1
{
  "doc": {
    "price": 229.99,
    "stock_quantity": 120
  }
}

// Update with script
POST /products/_update/1
{
  "script": {
    "source": "ctx._source.stock_quantity += params.count",
    "params": {
      "count": 10
    }
  }
}

// Update by query
POST /products/_update_by_query
{
  "query": {
    "term": {
      "category": "Electronics"
    }
  },
  "script": {
    "source": "ctx._source.price *= 0.9"  // 10% discount
  }
}
