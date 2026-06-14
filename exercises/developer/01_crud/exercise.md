# Elasticsearch CRUD Operations Exercise

## Overview

This exercise demonstrates how to perform CRUD (Create, Read, Update, Delete)
operations in Elasticsearch using four different methods:

1. Kibana Dev Tools UI
1. curl (command line)
1. Python with requests library
1. Python with elasticsearch client

## Prerequisites

- Elasticsearch running on `localhost:9200`
- Kibana running on `localhost:5601` (for Method 1)
- Python 3.7+ installed (for Methods 3 & 4)
- Elasticsearch running with security disabled (plain HTTP, no authentication)

### Setup Test Environment

See [`01_setup_environment.sh`](./01_setup_environment.sh)

## Sample Data Structure

We'll work with a simple e-commerce product catalog:
See [`02_sample_document.json`](./02_sample_document.json)

---

## Method 1: Kibana Dev Tools UI

### Access Kibana Dev Tools

1. Open browser: `http://localhost:5601`
1. No login required (security is disabled)
1. Navigate to **Management → Dev Tools** (or use shortcut: `Ctrl+I`)

### 1.1 Create an Index

See [`03_create_index.js`](./03_create_index.js)

### 1.2 Insert Single Document

See [`04_insert_document.js`](./04_insert_document.js)

### 1.3 Bulk Insert Documents

See [`05_bulk_insert.js`](./05_bulk_insert.js)

### 1.4 Search/Read Documents

See [`06_search_documents.js`](./06_search_documents.js)

### 1.5 Update Documents

See [`07_update_documents.js`](./07_update_documents.js)

### 1.6 Delete Documents

See [`08_delete_documents.js`](./08_delete_documents.js)

---

## Method 2: curl (Command Line)

### 2.1 Create an Index

See [`09_create_index.sh`](./09_create_index.sh)

### 2.2 Insert Single Document

See [`10_insert_document.sh`](./10_insert_document.sh)

### 2.3 Bulk Insert Documents

See [`11_bulk_insert.sh`](./11_bulk_insert.sh)

### 2.4 Search/Read Documents

See [`12_search_documents.sh`](./12_search_documents.sh)

### 2.5 Update Documents

See [`13_update_documents.sh`](./13_update_documents.sh)

### 2.6 Delete Documents

See [`14_delete_documents.sh`](./14_delete_documents.sh)

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

See [`15_requests_setup.py`](./15_requests_setup.py)

### 3.2 Create Index

See [`16_requests_create_index.py`](./16_requests_create_index.py)

### 3.3 Insert Documents

See [`17_requests_insert_documents.py`](./17_requests_insert_documents.py)

### 3.4 Search/Read Documents

See [`18_requests_search_documents.py`](./18_requests_search_documents.py)

### 3.5 Update Documents

See [`19_requests_update_documents.py`](./19_requests_update_documents.py)

### 3.6 Delete Documents

See [`20_requests_delete_documents.py`](./20_requests_delete_documents.py)

---

## Method 4: Python with elasticsearch Client

### 4.1 Setup and Configuration

See [`21_client_setup.py`](./21_client_setup.py)

### 4.2 Create Index

See [`22_client_create_index.py`](./22_client_create_index.py)

### 4.3 Insert Documents

See [`23_client_insert_documents.py`](./23_client_insert_documents.py)

### 4.4 Search/Read Documents

See [`24_client_search_documents.py`](./24_client_search_documents.py)

### 4.5 Update Documents

See [`25_client_update_documents.py`](./25_client_update_documents.py)

### 4.6 Delete Documents

See [`26_client_delete_documents.py`](./26_client_delete_documents.py)

### 4.7 Advanced Operations

See [`27_client_advanced_operations.py`](./27_client_advanced_operations.py)

---

## Complete Working Example

Here's a complete script that demonstrates all CRUD operations:

See [`28_complete_crud_demo.py`](./28_complete_crud_demo.py)

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
1. **Set refresh=false** for bulk operations, then refresh once at the end
1. **Use scroll API or search_after** for large result sets
1. **Implement proper error handling** and retry logic
1. **Use connection pooling** in production applications
1. **Set appropriate timeouts** for long-running operations
1. **Monitor cluster health** before performing heavy operations
1. **Use index aliases** for zero-downtime reindexing
1. **Implement proper authentication** and use HTTPS in production
1. **Version your mappings** and maintain backward compatibility

---

## Troubleshooting Common Issues

### Connection Refused

See [`29_troubleshoot_connection_refused.sh`](./29_troubleshoot_connection_refused.sh)

### Authentication Failed

See [`30_troubleshoot_authentication.sh`](./30_troubleshoot_authentication.sh)

### Document Not Found Immediately After Insert

See [`31_troubleshoot_refresh_visibility.py`](./31_troubleshoot_refresh_visibility.py)

### Mapping Conflicts

See [`32_troubleshoot_mapping_conflicts.py`](./32_troubleshoot_mapping_conflicts.py)

---

## Next Steps

1. **Learn about Index Templates** for automatic mapping application
1. **Explore Aggregations** for analytics
1. **Implement Search Suggestions** using completion suggester
1. **Set up Index Lifecycle Management** (ILM) for data retention
1. **Learn about Elasticsearch Security** features
1. **Explore Elasticsearch SQL** for SQL-like queries
1. **Implement Geographic Queries** for location-based search
1. **Use Percolator** for reverse search scenarios
1. **Set up Cross-Cluster Search** for distributed systems
1. **Monitor Performance** using Elasticsearch APIs
