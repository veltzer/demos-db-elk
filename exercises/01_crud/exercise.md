# Elasticsearch CRUD Operations Exercise

## Overview
This exercise demonstrates how to perform CRUD (Create, Read, Update, Delete) operations in Elasticsearch using four different methods:
1. Kibana Dev Tools UI
2. curl (command line)
3. Python with requests library
4. Python with elasticsearch client

## Prerequisites

- Elasticsearch running on `localhost:9200`
- Kibana running on `localhost:5601` (for Method 1)
- Python 3.7+ installed (for Methods 3 & 4)
- Basic authentication credentials (default: elastic/your-password)

### Setup Test Environment
```bash
# Verify Elasticsearch is running
curl -X GET "localhost:9200" -u elastic:your-password

# Install Python dependencies (for methods 3 & 4)
pip install requests elasticsearch
```

## Sample Data Structure

We'll work with a simple e-commerce product catalog:
```json
{
  "product_id": "PROD001",
  "name": "Wireless Bluetooth Headphones",
  "category": "Electronics",
  "price": 79.99,
  "stock_quantity": 150,
  "description": "High-quality wireless headphones with noise cancellation",
  "tags": ["wireless", "bluetooth", "audio"],
  "created_at": "2024-01-15T10:30:00Z",
  "in_stock": true
}
```

---

## Method 1: Kibana Dev Tools UI

### Access Kibana Dev Tools
1. Open browser: `http://localhost:5601`
2. Login with your credentials
3. Navigate to **Management → Dev Tools** (or use shortcut: `Ctrl+I`)

### 1.1 Create an Index
```javascript
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
```

### 1.2 Insert Single Document
```javascript
// Insert with auto-generated ID
POST /products/_doc
{
  "product_id": "PROD001",
  "name": "Wireless Bluetooth Headphones",
  "category": "Electronics",
  "price": 79.99,
  "stock_quantity": 150,
  "description": "High-quality wireless headphones with noise cancellation",
  "tags": ["wireless", "bluetooth", "audio"],
  "created_at": "2024-01-15T10:30:00Z",
  "in_stock": true
}

// Insert with specific ID
PUT /products/_doc/1
{
  "product_id": "PROD002",
  "name": "Smart Watch Pro",
  "category": "Electronics",
  "price": 299.99,
  "stock_quantity": 75,
  "description": "Advanced fitness tracking and health monitoring",
  "tags": ["smartwatch", "fitness", "health"],
  "created_at": "2024-01-16T14:20:00Z",
  "in_stock": true
}
```

### 1.3 Bulk Insert Documents
```javascript
POST /products/_bulk
{ "index": { "_id": "2" } }
{ "product_id": "PROD003", "name": "Yoga Mat Premium", "category": "Sports", "price": 34.99, "stock_quantity": 200, "description": "Non-slip exercise mat", "tags": ["yoga", "fitness"], "created_at": "2024-01-17T09:00:00Z", "in_stock": true }
{ "index": { "_id": "3" } }
{ "product_id": "PROD004", "name": "Coffee Maker Deluxe", "category": "Appliances", "price": 129.99, "stock_quantity": 50, "description": "Programmable coffee maker with thermal carafe", "tags": ["coffee", "kitchen"], "created_at": "2024-01-18T11:30:00Z", "in_stock": true }
{ "index": { "_id": "4" } }
{ "product_id": "PROD005", "name": "Running Shoes", "category": "Sports", "price": 89.99, "stock_quantity": 0, "description": "Professional running shoes", "tags": ["running", "sports"], "created_at": "2024-01-19T16:45:00Z", "in_stock": false }
```

### 1.4 Search/Read Documents
```javascript
// Get specific document
GET /products/_doc/1

// Search all documents
GET /products/_search
{
  "query": {
    "match_all": {}
  }
}

// Search with criteria
GET /products/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "category": "Electronics" } },
        { "range": { "price": { "gte": 50, "lte": 300 } } }
      ]
    }
  }
}

// Search with aggregations
GET /products/_search
{
  "size": 0,
  "aggs": {
    "category_count": {
      "terms": {
        "field": "category"
      }
    },
    "avg_price": {
      "avg": {
        "field": "price"
      }
    }
  }
}
```

### 1.5 Update Documents
```javascript
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
```

### 1.6 Delete Documents
```javascript
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
```

---

## Method 2: curl (Command Line)

### 2.1 Create an Index
```bash
curl -X PUT "localhost:9200/products" \
  -H 'Content-Type: application/json' \
  -u elastic:your-password \
  -d '{
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
  }'
```

### 2.2 Insert Single Document
```bash
# Insert with auto-generated ID
curl -X POST "localhost:9200/products/_doc" \
  -H 'Content-Type: application/json' \
  -u elastic:your-password \
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
  -u elastic:your-password \
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
```

### 2.3 Bulk Insert Documents
```bash
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
  -u elastic:your-password \
  --data-binary @bulk_products.json
```

### 2.4 Search/Read Documents
```bash
# Get specific document
curl -X GET "localhost:9200/products/_doc/1?pretty" \
  -u elastic:your-password

# Search all documents
curl -X GET "localhost:9200/products/_search?pretty" \
  -H 'Content-Type: application/json' \
  -u elastic:your-password \
  -d '{
    "query": {
      "match_all": {}
    }
  }'

# Search with criteria
curl -X GET "localhost:9200/products/_search?pretty" \
  -H 'Content-Type: application/json' \
  -u elastic:your-password \
  -d '{
    "query": {
      "bool": {
        "must": [
          { "match": { "category": "Electronics" } },
          { "range": { "price": { "gte": 50, "lte": 300 } } }
        ]
      }
    }
  }'

# Simple query string search
curl -X GET "localhost:9200/products/_search?q=category:Electronics&pretty" \
  -u elastic:your-password
```

### 2.5 Update Documents
```bash
# Full update
curl -X PUT "localhost:9200/products/_doc/1" \
  -H 'Content-Type: application/json' \
  -u elastic:your-password \
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
  -u elastic:your-password \
  -d '{
    "doc": {
      "price": 229.99,
      "stock_quantity": 120
    }
  }'

# Update with script
curl -X POST "localhost:9200/products/_update/1" \
  -H 'Content-Type: application/json' \
  -u elastic:your-password \
  -d '{
    "script": {
      "source": "ctx._source.stock_quantity += params.count",
      "params": {
        "count": 10
      }
    }
  }'
```

### 2.6 Delete Documents
```bash
# Delete single document
curl -X DELETE "localhost:9200/products/_doc/1" \
  -u elastic:your-password

# Delete by query
curl -X POST "localhost:9200/products/_delete_by_query" \
  -H 'Content-Type: application/json' \
  -u elastic:your-password \
  -d '{
    "query": {
      "term": {
        "in_stock": false
      }
    }
  }'

# Delete entire index
curl -X DELETE "localhost:9200/products" \
  -u elastic:your-password
```

---

## Notes about python and virtual env

- To get virtualenv support:
	`$ sudo apt install python3-virtualenv`

- To create a virtualenv:
	`$ virtualenv .venv`

- To enter the virtual env:
	`$ source .venv/bin/activate`

- To exit the virtual env:
	`$ deactivate`

- To install al package in the virtual env:
	`$ pip install [pkg_name]`

---

## Method 3: Python with requests Library

### 3.1 Setup and Configuration
```python
#!/usr/bin/env python3
"""
Elasticsearch CRUD operations using requests library
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
ES_HOST = "localhost"
ES_PORT = 9200
ES_USER = "elastic"
ES_PASSWORD = "your-password"
ES_URL = f"http://{ES_HOST}:{ES_PORT}"
INDEX_NAME = "products"

# Session with authentication
session = requests.Session()
session.auth = (ES_USER, ES_PASSWORD)
session.headers.update({'Content-Type': 'application/json'})

def pretty_print(response):
    """Pretty print JSON response"""
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
```

### 3.2 Create Index
```python
def create_index():
    """Create products index with mappings"""
    mappings = {
        "mappings": {
            "properties": {
                "product_id": {"type": "keyword"},
                "name": {"type": "text"},
                "category": {"type": "keyword"},
                "price": {"type": "float"},
                "stock_quantity": {"type": "integer"},
                "description": {"type": "text"},
                "tags": {"type": "keyword"},
                "created_at": {"type": "date"},
                "in_stock": {"type": "boolean"}
            }
        }
    }
    
    response = session.put(
        f"{ES_URL}/{INDEX_NAME}",
        data=json.dumps(mappings)
    )
    
    print(f"Index creation status: {response.status_code}")
    pretty_print(response)
    return response

# Execute
create_index()
```

### 3.3 Insert Documents
```python
def insert_single_document(doc_id: Optional[str] = None):
    """Insert a single document"""
    document = {
        "product_id": "PROD001",
        "name": "Wireless Bluetooth Headphones",
        "category": "Electronics",
        "price": 79.99,
        "stock_quantity": 150,
        "description": "High-quality wireless headphones with noise cancellation",
        "tags": ["wireless", "bluetooth", "audio"],
        "created_at": datetime.now().isoformat(),
        "in_stock": True
    }
    
    if doc_id:
        # Insert with specific ID
        url = f"{ES_URL}/{INDEX_NAME}/_doc/{doc_id}"
        response = session.put(url, data=json.dumps(document))
    else:
        # Insert with auto-generated ID
        url = f"{ES_URL}/{INDEX_NAME}/_doc"
        response = session.post(url, data=json.dumps(document))
    
    print(f"Insert status: {response.status_code}")
    pretty_print(response)
    return response

def bulk_insert_documents():
    """Bulk insert multiple documents"""
    products = [
        {
            "product_id": "PROD002",
            "name": "Smart Watch Pro",
            "category": "Electronics",
            "price": 299.99,
            "stock_quantity": 75,
            "description": "Advanced fitness tracking",
            "tags": ["smartwatch", "fitness"],
            "created_at": datetime.now().isoformat(),
            "in_stock": True
        },
        {
            "product_id": "PROD003",
            "name": "Yoga Mat Premium",
            "category": "Sports",
            "price": 34.99,
            "stock_quantity": 200,
            "description": "Non-slip exercise mat",
            "tags": ["yoga", "fitness"],
            "created_at": datetime.now().isoformat(),
            "in_stock": True
        },
        {
            "product_id": "PROD004",
            "name": "Coffee Maker Deluxe",
            "category": "Appliances",
            "price": 129.99,
            "stock_quantity": 50,
            "description": "Programmable coffee maker",
            "tags": ["coffee", "kitchen"],
            "created_at": datetime.now().isoformat(),
            "in_stock": True
        }
    ]
    
    # Build bulk request body
    bulk_data = []
    for i, product in enumerate(products, start=2):
        bulk_data.append(json.dumps({"index": {"_id": str(i)}}))
        bulk_data.append(json.dumps(product))
    
    # Join with newlines (NDJSON format)
    bulk_body = '\n'.join(bulk_data) + '\n'
    
    # Send bulk request
    response = session.post(
        f"{ES_URL}/{INDEX_NAME}/_bulk",
        data=bulk_body,
        headers={'Content-Type': 'application/x-ndjson'}
    )
    
    print(f"Bulk insert status: {response.status_code}")
    result = response.json()
    print(f"Errors: {result.get('errors', False)}")
    print(f"Items processed: {len(result.get('items', []))}")
    return response

# Execute
insert_single_document("1")
bulk_insert_documents()
```

### 3.4 Search/Read Documents
```python
def get_document(doc_id: str):
    """Get a specific document by ID"""
    response = session.get(f"{ES_URL}/{INDEX_NAME}/_doc/{doc_id}")
    print(f"Get document status: {response.status_code}")
    pretty_print(response)
    return response

def search_documents(query: Dict = None):
    """Search documents with optional query"""
    if query is None:
        query = {"query": {"match_all": {}}}
    
    response = session.get(
        f"{ES_URL}/{INDEX_NAME}/_search",
        data=json.dumps(query)
    )
    
    print(f"Search status: {response.status_code}")
    result = response.json()
    
    # Display results
    hits = result.get('hits', {}).get('hits', [])
    print(f"Total hits: {result.get('hits', {}).get('total', {}).get('value', 0)}")
    
    for hit in hits:
        print(f"\nID: {hit['_id']}")
        print(f"Score: {hit['_score']}")
        print(f"Source: {json.dumps(hit['_source'], indent=2)}")
    
    return response

def search_with_criteria():
    """Search with specific criteria"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"category": "Electronics"}},
                    {"range": {"price": {"gte": 50, "lte": 300}}}
                ]
            }
        },
        "sort": [{"price": "asc"}],
        "size": 10
    }
    
    return search_documents(query)

# Execute
get_document("1")
search_documents()
search_with_criteria()
```

### 3.5 Update Documents
```python
def update_document_full(doc_id: str):
    """Full document update (replace)"""
    updated_doc = {
        "product_id": "PROD001",
        "name": "Wireless Bluetooth Headphones - Premium",
        "category": "Electronics",
        "price": 99.99,
        "stock_quantity": 175,
        "description": "Premium wireless headphones with ANC",
        "tags": ["wireless", "bluetooth", "audio", "premium"],
        "created_at": datetime.now().isoformat(),
        "in_stock": True
    }
    
    response = session.put(
        f"{ES_URL}/{INDEX_NAME}/_doc/{doc_id}",
        data=json.dumps(updated_doc)
    )
    
    print(f"Full update status: {response.status_code}")
    pretty_print(response)
    return response

def update_document_partial(doc_id: str):
    """Partial document update"""
    update_data = {
        "doc": {
            "price": 89.99,
            "stock_quantity": 200,
            "tags": ["wireless", "bluetooth", "audio", "sale"]
        }
    }
    
    response = session.post(
        f"{ES_URL}/{INDEX_NAME}/_update/{doc_id}",
        data=json.dumps(update_data)
    )
    
    print(f"Partial update status: {response.status_code}")
    pretty_print(response)
    return response

def update_by_query():
    """Update multiple documents by query"""
    update_query = {
        "query": {
            "term": {"category": "Electronics"}
        },
        "script": {
            "source": "ctx._source.price *= params.discount",
            "params": {"discount": 0.9}  # 10% discount
        }
    }
    
    response = session.post(
        f"{ES_URL}/{INDEX_NAME}/_update_by_query",
        data=json.dumps(update_query)
    )
    
    print(f"Update by query status: {response.status_code}")
    pretty_print(response)
    return response

# Execute
update_document_full("1")
update_document_partial("1")
update_by_query()
```

### 3.6 Delete Documents
```python
def delete_document(doc_id: str):
    """Delete a single document"""
    response = session.delete(f"{ES_URL}/{INDEX_NAME}/_doc/{doc_id}")
    print(f"Delete document status: {response.status_code}")
    pretty_print(response)
    return response

def delete_by_query():
    """Delete documents by query"""
    delete_query = {
        "query": {
            "term": {"in_stock": False}
        }
    }
    
    response = session.post(
        f"{ES_URL}/{INDEX_NAME}/_delete_by_query",
        data=json.dumps(delete_query)
    )
    
    print(f"Delete by query status: {response.status_code}")
    pretty_print(response)
    return response

def delete_index():
    """Delete entire index"""
    response = session.delete(f"{ES_URL}/{INDEX_NAME}")
    print(f"Delete index status: {response.status_code}")
    pretty_print(response)
    return response

# Execute
delete_document("1")
delete_by_query()
# delete_index()  # Uncomment to delete entire index
```

---

## Method 4: Python with elasticsearch Client

### 4.1 Setup and Configuration
```python
#!/usr/bin/env python3
"""
Elasticsearch CRUD operations using official elasticsearch-py client
"""

from elasticsearch import Elasticsearch, helpers
from datetime import datetime
import json
from typing import Dict, List, Optional

# Initialize client
es = Elasticsearch(
    ['http://localhost:9200'],
    basic_auth=('elastic', 'your-password'),
    verify_certs=False  # Set to True in production with proper certificates
)

# Verify connection
if es.ping():
    print("Connected to Elasticsearch")
    print(es.info())
else:
    print("Could not connect to Elasticsearch")
    exit(1)

INDEX_NAME = "products"
```

### 4.2 Create Index
```python
def create_index():
    """Create products index with mappings"""
    mappings = {
        "mappings": {
            "properties": {
                "product_id": {"type": "keyword"},
                "name": {"type": "text"},
                "category": {"type": "keyword"},
                "price": {"type": "float"},
                "stock_quantity": {"type": "integer"},
                "description": {"type": "text"},
                "tags": {"type": "keyword"},
                "created_at": {"type": "date"},
                "in_stock": {"type": "boolean"}
            }
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }
    
    # Delete index if exists
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print(f"Deleted existing index: {INDEX_NAME}")
    
    # Create index
    response = es.indices.create(index=INDEX_NAME, body=mappings)
    print(f"Index created: {response}")
    return response

# Execute
create_index()
```

### 4.3 Insert Documents
```python
def insert_single_document():
    """Insert a single document"""
    document = {
        "product_id": "PROD001",
        "name": "Wireless Bluetooth Headphones",
        "category": "Electronics",
        "price": 79.99,
        "stock_quantity": 150,
        "description": "High-quality wireless headphones with noise cancellation",
        "tags": ["wireless", "bluetooth", "audio"],
        "created_at": datetime.now(),
        "in_stock": True
    }
    
    # Insert with auto-generated ID
    response = es.index(index=INDEX_NAME, document=document)
    print(f"Document inserted (auto ID): {response['_id']}")
    
    # Insert with specific ID
    response = es.index(index=INDEX_NAME, id="1", document=document)
    print(f"Document inserted (ID=1): {response['result']}")
    
    return response

def bulk_insert_documents():
    """Bulk insert multiple documents using helpers"""
    products = [
        {
            "_index": INDEX_NAME,
            "_id": "2",
            "_source": {
                "product_id": "PROD002",
                "name": "Smart Watch Pro",
                "category": "Electronics",
                "price": 299.99,
                "stock_quantity": 75,
                "description": "Advanced fitness tracking",
                "tags": ["smartwatch", "fitness"],
                "created_at": datetime.now(),
                "in_stock": True
            }
        },
        {
            "_index": INDEX_NAME,
            "_id": "3",
            "_source": {
                "product_id": "PROD003",
                "name": "Yoga Mat Premium",
                "category": "Sports",
                "price": 34.99,
                "stock_quantity": 200,
                "description": "Non-slip exercise mat",
                "tags": ["yoga", "fitness"],
                "created_at": datetime.now(),
                "in_stock": True
            }
        },
        {
            "_index": INDEX_NAME,
            "_id": "4",
            "_source": {
                "product_id": "PROD004",
                "name": "Coffee Maker Deluxe",
                "category": "Appliances",
                "price": 129.99,
                "stock_quantity": 50,
                "description": "Programmable coffee maker",
                "tags": ["coffee", "kitchen"],
                "created_at": datetime.now(),
                "in_stock": True
            }
        },
        {
            "_index": INDEX_NAME,
            "_id": "5",
            "_source": {
                "product_id": "PROD005",
                "name": "Running Shoes",
                "category": "Sports",
                "price": 89.99,
                "stock_quantity": 0,
                "description": "Professional running shoes",
                "tags": ["running", "sports"],
                "created_at": datetime.now(),
                "in_stock": False
            }
        }
    ]
    
    # Use helpers for efficient bulk operations
    success, failed = helpers.bulk(es, products, stats_only=True)
    print(f"Bulk insert - Success: {success}, Failed: {failed}")
    
    return success, failed

def bulk_insert_generator():
    """Bulk insert using generator (memory efficient for large datasets)"""
    def generate_products():
        for i in range(6, 11):
            yield {
                "_index": INDEX_NAME,
                "_id": str(i),
                "_source": {
                    "product_id": f"PROD{i:03d}",
                    "name": f"Product {i}",
                    "category": "General",
                    "price": 50.00 + (i * 10),
                    "stock_quantity": i * 10,
                    "description": f"Description for product {i}",
                    "tags": ["general"],
                    "created_at": datetime.now(),
                    "in_stock": True
                }
            }
    
    success, failed = helpers.bulk(es, generate_products(), stats_only=True)
    print(f"Bulk generator insert - Success: {success}, Failed: {failed}")
    return success, failed

# Execute
insert_single_document()
bulk_insert_documents()
bulk_insert_generator()
```

### 4.4 Search/Read Documents
```python
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
```

### 4.5 Update Documents
```python
def update_document_full(doc_id: str):
    """Full document update (replace)"""
    updated_doc = {
        "product_id": "PROD001",
        "name": "Wireless Bluetooth Headphones - Premium Edition",
        "category": "Electronics",
        "price": 119.99,
        "stock_quantity": 100,
        "description": "Premium wireless headphones with advanced ANC technology",
        "tags": ["wireless", "bluetooth", "audio", "premium", "anc"],
        "created_at": datetime.now(),
        "in_stock": True,
        "last_updated": datetime.now()
    }
    
    response = es.index(index=INDEX_NAME, id=doc_id, document=updated_doc)
    print(f"Full update result: {response['result']}")
    return response

def update_document_partial(doc_id: str):
    """Partial document update"""
    update_body = {
        "doc": {
            "price": 109.99,
            "stock_quantity": 85,
            "last_updated": datetime.now()
        }
    }
    
    response = es.update(index=INDEX_NAME, id=doc_id, body=update_body)
    print(f"Partial update result: {response['result']}")
    return response

def update_with_script(doc_id: str):
    """Update using script"""
    script_body = {
        "script": {
            "source": """
                ctx._source.stock_quantity += params.quantity;
                ctx._source.last_updated = params.now;
                if (ctx._source.stock_quantity <= 0) {
                    ctx._source.in_stock = false;
                } else {
                    ctx._source.in_stock = true;
                }
            """,
            "params": {
                "quantity": -10,  # Reduce stock by 10
                "now": datetime.now().isoformat()
            }
        }
    }
    
    response = es.update(index=INDEX_NAME, id=doc_id, body=script_body)
    print(f"Script update result: {response['result']}")
    return response

def update_by_query():
    """Update multiple documents by query"""
    # Apply 15% discount to all Electronics
    update_query = {
        "script": {
            "source": """
                ctx._source.price = ctx._source.price * params.discount;
                ctx._source.tags.add(params.tag);
                ctx._source.last_updated = params.now;
            """,
            "params": {
                "discount": 0.85,
                "tag": "sale",
                "now": datetime.now().isoformat()
            }
        },
        "query": {
            "term": {"category": "Electronics"}
        }
    }
    
    response = es.update_by_query(index=INDEX_NAME, body=update_query)
    print(f"Update by query - Updated: {response['updated']}, Failed: {response['failures']}")
    return response

def upsert_document():
    """Upsert - Update if exists, insert if not"""
    doc_id = "99"
    upsert_body = {
        "doc": {
            "price": 159.99,
            "stock_quantity": 25,
            "last_updated": datetime.now()
        },
        "upsert": {
            "product_id": "PROD099",
            "name": "New Product via Upsert",
            "category": "Electronics",
            "price": 159.99,
            "stock_quantity": 25,
            "description": "Created via upsert operation",
            "tags": ["new", "upsert"],
            "created_at": datetime.now(),
            "in_stock": True
        }
    }
    
    response = es.update(index=INDEX_NAME, id=doc_id, body=upsert_body)
    print(f"Upsert result: {response['result']} (version: {response['_version']})")
    return response

# Execute
update_document_full("1")
update_document_partial("1")
update_with_script("1")
update_by_query()
upsert_document()
```

### 4.6 Delete Documents
```python
def delete_document(doc_id: str):
    """Delete a single document"""
    try:
        response = es.delete(index=INDEX_NAME, id=doc_id)
        print(f"Deleted document {doc_id}: {response['result']}")
        return response
    except Exception as e:
        print(f"Error deleting document: {e}")
        return None

def delete_by_query():
    """Delete documents by query"""
    # Delete all out-of-stock items
    delete_query = {
        "query": {
            "term": {"in_stock": False}
        }
    }
    
    response = es.delete_by_query(index=INDEX_NAME, body=delete_query)
    print(f"Delete by query - Deleted: {response['deleted']}, Failed: {response['failures']}")
    return response

def delete_with_refresh():
    """Delete and immediately refresh index"""
    # Delete and refresh to make changes immediately visible
    response = es.delete(index=INDEX_NAME, id="2", refresh=True)
    print(f"Deleted with refresh: {response['result']}")
    return response

def delete_index():
    """Delete entire index"""
    response = es.indices.delete(index=INDEX_NAME)
    print(f"Index {INDEX_NAME} deleted: {response['acknowledged']}")
    return response

# Execute
delete_document("99")
delete_by_query()
# delete_with_refresh()  # Uncomment to test
# delete_index()  # Uncomment to delete entire index
```

### 4.7 Advanced Operations
```python
def mget_documents():
    """Get multiple documents in one request"""
    doc_ids = ["1", "2", "3"]
    response = es.mget(
        index=INDEX_NAME,
        body={"ids": doc_ids}
    )
    
    print("Multiple Get Results:")
    for doc in response['docs']:
        if doc['found']:
            print(f"- {doc['_id']}: {doc['_source']['name']}")
        else:
            print(f"- {doc['_id']}: Not found")
    
    return response

def count_documents():
    """Count documents matching a query"""
    # Count all documents
    total = es.count(index=INDEX_NAME)['count']
    print(f"Total documents: {total}")
    
    # Count with query
    query = {"query": {"term": {"category": "Electronics"}}}
    electronics_count = es.count(index=INDEX_NAME, body=query)['count']
    print(f"Electronics products: {electronics_count}")
    
    return total, electronics_count

def scroll_through_results():
    """Use scroll API for large result sets"""
    # Initial search with scroll
    response = es.search(
        index=INDEX_NAME,
        scroll='2m',  # Keep scroll context for 2 minutes
        size=2,  # Get 2 documents per batch
        body={"query": {"match_all": {}}}
    )
    
    scroll_id = response['_scroll_id']
    results = response['hits']['hits']
    
    print(f"Scrolling through results (batch size: 2)")
    batch = 1
    
    while results:
        print(f"\nBatch {batch}:")
        for hit in results:
            print(f"- {hit['_source']['name']}")
        
        # Get next batch
        response = es.scroll(scroll_id=scroll_id, scroll='2m')
        scroll_id = response['_scroll_id']
        results = response['hits']['hits']
        batch += 1
    
    # Clear scroll context
    es.clear_scroll(scroll_id=scroll_id)
    print("\nScroll context cleared")

def reindex_documents():
    """Reindex documents to a new index"""
    new_index = f"{INDEX_NAME}_v2"
    
    # Create new index with updated mappings
    es.indices.create(
        index=new_index,
        body={
            "mappings": {
                "properties": {
                    "product_id": {"type": "keyword"},
                    "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "category": {"type": "keyword"},
                    "price": {"type": "float"},
                    "stock_quantity": {"type": "integer"},
                    "description": {"type": "text"},
                    "tags": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "in_stock": {"type": "boolean"},
                    "last_updated": {"type": "date"}
                }
            }
        }
    )
    
    # Reindex
    response = es.reindex(
        body={
            "source": {"index": INDEX_NAME},
            "dest": {"index": new_index}
        }
    )
    
    print(f"Reindexed {response['total']} documents to {new_index}")
    
    # Clean up - delete new index
    es.indices.delete(index=new_index)
    print(f"Cleaned up {new_index}")
    
    return response

# Execute advanced operations
mget_documents()
count_documents()
scroll_through_results()
reindex_documents()
```

---

## Complete Working Example

Here's a complete script that demonstrates all CRUD operations:

```python
#!/usr/bin/env python3
"""
Complete Elasticsearch CRUD example
Run this script to see all operations in action
"""

from elasticsearch import Elasticsearch, helpers
from datetime import datetime
import time
import json

# Initialize connection
es = Elasticsearch(
    ['http://localhost:9200'],
    basic_auth=('elastic', 'your-password'),
    verify_certs=False
)

INDEX_NAME = "products_demo"

def run_complete_demo():
    """Run complete CRUD demonstration"""
    
    print("=" * 50)
    print("ELASTICSEARCH CRUD OPERATIONS DEMO")
    print("=" * 50)
    
    # 1. CREATE INDEX
    print("\n1. CREATING INDEX")
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
    
    es.indices.create(
        index=INDEX_NAME,
        body={
            "mappings": {
                "properties": {
                    "name": {"type": "text"},
                    "price": {"type": "float"},
                    "category": {"type": "keyword"},
                    "in_stock": {"type": "boolean"}
                }
            }
        }
    )
    print(f"✓ Index '{INDEX_NAME}' created")
    
    # 2. INSERT DOCUMENTS
    print("\n2. INSERTING DOCUMENTS")
    products = [
        {"name": "Laptop", "price": 999.99, "category": "Electronics", "in_stock": True},
        {"name": "Mouse", "price": 29.99, "category": "Electronics", "in_stock": True},
        {"name": "Keyboard", "price": 79.99, "category": "Electronics", "in_stock": False},
        {"name": "Monitor", "price": 299.99, "category": "Electronics", "in_stock": True},
        {"name": "Desk Chair", "price": 199.99, "category": "Furniture", "in_stock": True}
    ]
    
    for i, product in enumerate(products, 1):
        es.index(index=INDEX_NAME, id=str(i), document=product)
        print(f"✓ Inserted: {product['name']}")
    
    # Refresh index to make documents searchable immediately
    es.indices.refresh(index=INDEX_NAME)
    
    # 3. READ/SEARCH DOCUMENTS
    print("\n3. SEARCHING DOCUMENTS")
    
    # Get specific document
    doc = es.get(index=INDEX_NAME, id="1")
    print(f"✓ Retrieved doc 1: {doc['_source']['name']}")
    
    # Search all
    results = es.search(index=INDEX_NAME, body={"query": {"match_all": {}}})
    print(f"✓ Total documents: {results['hits']['total']['value']}")
    
    # Search with filter
    results = es.search(
        index=INDEX_NAME,
        body={
            "query": {
                "bool": {
                    "must": [{"term": {"category": "Electronics"}}],
                    "filter": [{"term": {"in_stock": True}}]
                }
            }
        }
    )
    print(f"✓ Electronics in stock: {results['hits']['total']['value']}")
    
    # 4. UPDATE DOCUMENTS
    print("\n4. UPDATING DOCUMENTS")
    
    # Update price
    es.update(
        index=INDEX_NAME,
        id="1",
        body={"doc": {"price": 899.99}}
    )
    print("✓ Updated Laptop price to $899.99")
    
    # Update by query - add discount
    es.update_by_query(
        index=INDEX_NAME,
        body={
            "query": {"term": {"category": "Electronics"}},
            "script": {"source": "ctx._source.price *= 0.9"}
        }
    )
    print("✓ Applied 10% discount to all Electronics")
    
    # 5. DELETE DOCUMENTS
    print("\n5. DELETING DOCUMENTS")
    
    # Delete single document
    es.delete(index=INDEX_NAME, id="5")
    print("✓ Deleted document 5 (Desk Chair)")
    
    # Delete by query
    es.delete_by_query(
        index=INDEX_NAME,
        body={"query": {"term": {"in_stock": False}}}
    )
    print("✓ Deleted all out-of-stock items")
    
    # 6. FINAL COUNT
    print("\n6. FINAL STATUS")
    es.indices.refresh(index=INDEX_NAME)
    count = es.count(index=INDEX_NAME)['count']
    print(f"✓ Remaining documents: {count}")
    
    # 7. CLEANUP
    print("\n7. CLEANUP")
    es.indices.delete(index=INDEX_NAME)
    print(f"✓ Index '{INDEX_NAME}' deleted")
    
    print("\n" + "=" * 50)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 50)

if __name__ == "__main__":
    run_complete_demo()
```

---

## Comparison of Methods

### Kibana Dev Tools UI

**Pros:**
- Visual and interactive
- Syntax highlighting and auto-completion
- Immediate feedback
- Great for exploration and testing
- No programming knowledge required
- Built-in documentation

**Cons:**
- Manual process, not suitable for automation
- Limited to browser interface
- Not suitable for production applications
- No version control for queries

**Best for:** Development, testing, debugging, exploring data

### curl (Command Line)

**Pros:**
- Available on all Unix-like systems
- No additional dependencies
- Good for shell scripts
- Easy to integrate with CI/CD pipelines
- Direct HTTP interaction

**Cons:**
- Verbose syntax
- JSON formatting can be cumbersome
- Limited error handling
- Authentication handling can be complex

**Best for:** Shell scripts, quick tests, CI/CD pipelines, system administration

### Python with requests

**Pros:**
- Full control over HTTP requests
- Lightweight (only requires requests library)
- Easy to understand HTTP interactions
- Good for learning Elasticsearch REST API
- Flexible error handling

**Cons:**
- More boilerplate code
- Manual JSON handling
- No built-in Elasticsearch helpers
- Need to handle connection pooling manually

**Best for:** Custom applications, when you need fine control, learning purposes

### Python with elasticsearch client

**Pros:**
- Official client with full API support
- Built-in helpers (bulk operations, scroll, etc.)
- Connection pooling and retry logic
- Type hints and IDE support
- Pythonic interface
- Better error handling

**Cons:**
- Additional dependency
- Abstracts away HTTP details
- May have version compatibility issues
- Slightly higher learning curve

**Best for:** Production applications, complex operations, data pipelines

---

## Best Practices

1. **Always use bulk operations** for inserting/updating multiple documents
2. **Set refresh=false** for bulk operations, then refresh once at the end
3. **Use scroll API or search_after** for large result sets
4. **Implement proper error handling** and retry logic
5. **Use connection pooling** in production applications
6. **Set appropriate timeouts** for long-running operations
7. **Monitor cluster health** before performing heavy operations
8. **Use index aliases** for zero-downtime reindexing
9. **Implement proper authentication** and use HTTPS in production
10. **Version your mappings** and maintain backward compatibility

---

## Troubleshooting Common Issues

### Connection Refused
```python
# Check if Elasticsearch is running
curl -X GET "localhost:9200"

# Check if you're using the correct port and protocol
# Default is http://localhost:9200, not https
```

### Authentication Failed
```python
# Reset elastic user password
./bin/elasticsearch-reset-password -u elastic

# Or create a new user with appropriate permissions
```

### Document Not Found Immediately After Insert
```python
# Force refresh after insert
es.index(index=INDEX_NAME, id="1", document=doc, refresh=True)

# Or refresh the entire index
es.indices.refresh(index=INDEX_NAME)
```

### Mapping Conflicts
```python
# Check existing mappings
es.indices.get_mapping(index=INDEX_NAME)

# Reindex to new index with correct mappings if needed
```

---

## Next Steps

1. **Learn about Index Templates** for automatic mapping application
2. **Explore Aggregations** for analytics
3. **Implement Search Suggestions** using completion suggester
4. **Set up Index Lifecycle Management** (ILM) for data retention
5. **Learn about Elasticsearch Security** features
6. **Explore Elasticsearch SQL** for SQL-like queries
7. **Implement Geographic Queries** for location-based search
8. **Use Percolator** for reverse search scenarios
9. **Set up Cross-Cluster Search** for distributed systems
10. **Monitor Performance** using Elasticsearch APIs
