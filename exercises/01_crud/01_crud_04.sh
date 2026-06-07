#!/bin/bash -eu
# Create a file with bulk data
cat > bulk_products.json << 'EOF'
{ "index": { "_id": "2" } }
{ "product_id": "PROD003", "name": "Yoga Mat Premium", "category": "Sports", "price": 34.99, "stock_quantity": 200, "description": "Non-slip exercise mat", "tags": ["yoga", "fitness"], "created_at": "2024-01-17T09:00:00Z", "in_stock": true }
{ "index": { "_id": "3" } }
{ "product_id": "PROD004", "name": "Coffee Maker Deluxe", "category": "Appliances", "price": 129.99, "stock_quantity": 50, "description": "Programmable coffee maker", "tags": ["coffee", "kitchen"], "created_at": "2024-01-18T11:30:00Z", "in_stock": true }
{ "index": { "_id": "4" } }
{ "product_id": "PROD005", "name": "Running Shoes", "category": "Sports", "price": 89.99, "stock_quantity": 0, "description": "Professional running shoes", "tags": ["running", "sports"], "created_at": "2024-01-19T16:45:00Z", "in_stock": false }

EOF

# Execute bulk insert
curl -X POST "localhost:9200/products/_bulk" \
  -H 'Content-Type: application/x-ndjson' \
  --data-binary @bulk_products.json
