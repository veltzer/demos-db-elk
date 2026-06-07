#!/usr/bin/env node
// Delete single document
DELETE /products/_doc/1

// Delete by query
POST /products/_delete_by_query
{
  "query": {
    "term": {
      "in_stock": false
    }
  }
}

// Delete entire index
DELETE /products
