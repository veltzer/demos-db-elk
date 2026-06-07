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
- Elasticsearch running with security disabled (plain HTTP, no authentication)

### Setup Test Environment
See [`01_crud_01.sh`](./01_crud_01.sh)


## Sample Data Structure

We'll work with a simple e-commerce product catalog:
See [`01_crud_01.json`](./01_crud_01.json)


---

## Method 1: Kibana Dev Tools UI

### Access Kibana Dev Tools
1. Open browser: `http://localhost:5601`
2. Login with your credentials
3. Navigate to **Management → Dev Tools** (or use shortcut: `Ctrl+I`)

### 1.1 Create an Index
See [`01_crud_01.js`](./01_crud_01.js)


### 1.2 Insert Single Document
See [`01_crud_02.js`](./01_crud_02.js)


### 1.3 Bulk Insert Documents
See [`01_crud_03.js`](./01_crud_03.js)


### 1.4 Search/Read Documents
See [`01_crud_04.js`](./01_crud_04.js)


### 1.5 Update Documents
See [`01_crud_05.js`](./01_crud_05.js)


### 1.6 Delete Documents
See [`01_crud_06.js`](./01_crud_06.js)


---

## Method 2: curl (Command Line)

### 2.1 Create an Index
See [`01_crud_02.sh`](./01_crud_02.sh)


### 2.2 Insert Single Document
See [`01_crud_03.sh`](./01_crud_03.sh)


### 2.3 Bulk Insert Documents
See [`01_crud_04.sh`](./01_crud_04.sh)


### 2.4 Search/Read Documents
See [`01_crud_05.sh`](./01_crud_05.sh)


### 2.5 Update Documents
See [`01_crud_06.sh`](./01_crud_06.sh)


### 2.6 Delete Documents
See [`01_crud_07.sh`](./01_crud_07.sh)


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
See [`01_crud_01.py`](./01_crud_01.py)


### 3.2 Create Index
See [`01_crud_02.py`](./01_crud_02.py)


### 3.3 Insert Documents
See [`01_crud_03.py`](./01_crud_03.py)


### 3.4 Search/Read Documents
See [`01_crud_04.py`](./01_crud_04.py)


### 3.5 Update Documents
See [`01_crud_05.py`](./01_crud_05.py)


### 3.6 Delete Documents
See [`01_crud_06.py`](./01_crud_06.py)


---

## Method 4: Python with elasticsearch Client

### 4.1 Setup and Configuration
See [`01_crud_07.py`](./01_crud_07.py)


### 4.2 Create Index
See [`01_crud_08.py`](./01_crud_08.py)


### 4.3 Insert Documents
See [`01_crud_09.py`](./01_crud_09.py)


### 4.4 Search/Read Documents
See [`01_crud_10.py`](./01_crud_10.py)


### 4.5 Update Documents
See [`01_crud_11.py`](./01_crud_11.py)


### 4.6 Delete Documents
See [`01_crud_12.py`](./01_crud_12.py)


### 4.7 Advanced Operations
See [`01_crud_13.py`](./01_crud_13.py)


---

## Complete Working Example

Here's a complete script that demonstrates all CRUD operations:

See [`01_crud_14.py`](./01_crud_14.py)


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
See [`01_crud_08.sh`](./01_crud_08.sh)


### Authentication Failed
See [`01_crud_09.sh`](./01_crud_09.sh)


### Document Not Found Immediately After Insert
See [`01_crud_17.py`](./01_crud_17.py)


### Mapping Conflicts
See [`01_crud_18.py`](./01_crud_18.py)


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
