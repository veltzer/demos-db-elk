#!/usr/bin/env node
// In Kibana Dev Tools Console
PUT /products
{
  "mappings": {
    "properties": {
      "product_id": { "type": "keyword" },
      "name": { "type": "text" },
      "category": { "type": "keyword" },
      "price": { "type": "float" },
      "stock_quantity": { "type": "integer" },
      "description": { "type": "text" },
      "tags": { "type": "keyword" },
      "created_at": { "type": "date" },
      "in_stock": { "type": "boolean" }
    }
  }
}
