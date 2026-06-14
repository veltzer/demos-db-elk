# Elasticsearch CRUD Operations Exercise

## Overview

This exercise demonstrates how to perform CRUD (Create, Read, Update, Delete)
operations in Elasticsearch using four different methods:

1. Kibana Dev Tools UI
1. curl (command line)
1. Python with requests library
1. Python with elasticsearch client

Why teach the same operations four ways? Because Elasticsearch is, at its
core, just a REST API that speaks JSON over HTTP. Every tool here is sending
the exact same HTTP requests under the hood. Kibana Dev Tools is the friendly
front door, curl shows the raw HTTP, the requests library shows that raw HTTP
expressed in Python, and the official client wraps it all in a convenient,
Pythonic interface. Seeing one operation expressed four ways makes it clear
where the real boundary is: the API, not the tool. Once you understand the
API, you can switch tools freely depending on the job.

## Prerequisites

- Elasticsearch running on `localhost:9200`
- Kibana running on `localhost:5601` (for Method 1)
- Python 3.7+ installed (for Methods 3 & 4)
- Elasticsearch running with security disabled (plain HTTP, no authentication)

Note that this exercise runs Elasticsearch with security disabled, so there
is no login and traffic is plain HTTP. This keeps the focus on CRUD concepts.
In any real deployment you would enable authentication and use HTTPS, because
an open Elasticsearch endpoint exposes all your data to anyone who can reach
the port.

### Setup Test Environment

See [`01_setup_environment.sh`](./01_setup_environment.sh)

The setup script first runs a plain `GET` against the root of the cluster.
That root response is a health-check handshake: if Elasticsearch is up it
returns a JSON document with the cluster name, version, and the famous
tagline. If you instead see "connection refused", nothing else in this
exercise will work, so this is the first thing to confirm.

## Sample Data Structure

We'll work with a simple e-commerce product catalog:
See [`02_sample_document.json`](./02_sample_document.json)

Each document is just a JSON object. Unlike a relational table, there are no
rows and columns: a document is a self-contained record, and the field names
inside it become the schema. Notice that `tags` is an array and `price` is a
decimal. Elasticsearch handles both naturally, which is one reason it suits
flexible, nested data better than a rigid SQL table.

---

## Method 1: Kibana Dev Tools UI

Kibana Dev Tools is a console built into Kibana that lets you type
Elasticsearch requests in a compact form and run them with a single click.
It strips away the HTTP boilerplate: you write `PUT /products` instead of a
full `curl` command. Behind the scenes Kibana sends the very same HTTP
request to Elasticsearch, so anything you learn here transfers directly to
the other methods.

### Access Kibana Dev Tools

1. Open browser: `http://localhost:5601`
1. No login required (security is disabled)
1. Navigate to **Management → Dev Tools** (or use shortcut: `Ctrl+I`)

### 1.1 Create an Index

See [`03_create_index.js`](./03_create_index.js)

An index is the rough equivalent of a table: it is a named collection of
documents. The `mappings` section defines the type of each field, and this
is where a critical Elasticsearch concept appears. Notice that `name` and
`description` are `text`, while `category`, `tags`, and `product_id` are
`keyword`. A `text` field is broken into individual words (analyzed) so it
can support full-text search such as matching "wireless" inside a longer
title. A `keyword` field is stored whole, exactly as given, so it is right
for filtering, sorting, and aggregations on exact values like a category
name. Choosing `text` versus `keyword` is one of the most consequential
decisions in Elasticsearch, because mappings cannot be changed in place once
data exists.

You can let Elasticsearch guess types automatically (dynamic mapping), but
defining mappings explicitly up front, as done here, avoids surprises like a
date being treated as a plain string.

### 1.2 Insert Single Document

See [`04_insert_document.js`](./04_insert_document.js)

This step shows the two ways to create a document. `POST /products/_doc`
lets Elasticsearch generate a random unique ID for you, which is ideal for
log-like data where you never need to address a specific record again.
`PUT /products/_doc/1` assigns the ID `1` yourself, which you want when the
document corresponds to a known entity you will later read or update by ID.
A subtle but important consequence: repeating the same `PUT` with the same
ID overwrites the existing document, while repeated `POST` calls keep
creating new ones.

### 1.3 Bulk Insert Documents

See [`05_bulk_insert.js`](./05_bulk_insert.js)

The `_bulk` API packs many operations into a single request. Each operation
is two lines: an action line saying what to do (here `index` with an `_id`)
followed by the document itself. This newline-delimited format exists for
performance: sending one thousand documents in one bulk request is far
faster than one thousand separate requests, because it avoids the network
round-trip and request overhead of each individual call. This is why bulk
loading is the standard way to ingest data at scale.

### 1.4 Search/Read Documents

See [`06_search_documents.js`](./06_search_documents.js)

Reading comes in two flavors. Fetching by ID with `GET /products/_doc/1` is
a direct lookup and always returns the current document. The `_search`
endpoint is the real power of Elasticsearch: `match_all` returns everything,
a `bool` query with `must` clauses combines conditions (here an exact
category match plus a price range), and the final example sets `size: 0` and
uses `aggs` to compute analytics. Setting `size` to zero tells Elasticsearch
you want only the aggregated numbers, not the matching documents themselves,
which makes dashboards and summaries efficient.

### 1.5 Update Documents

See [`07_update_documents.js`](./07_update_documents.js)

Updates reveal an important truth: Elasticsearch documents are immutable
under the hood. There is no in-place edit. A full `PUT` to an existing ID
actually replaces the whole document and silently drops any field you omit.
A partial update via `_update` with a `doc` block is more convenient, but
internally Elasticsearch still fetches the old document, merges your
changes, deletes the old version, and indexes a new one. The script-based
update lets you compute the new value from the old (incrementing stock), and
`_update_by_query` applies a change to every matching document at once, such
as discounting all electronics. Use the last one with care, since it can
touch a large number of documents in a single call.

### 1.6 Delete Documents

See [`08_delete_documents.js`](./08_delete_documents.js)

Deletion mirrors the read operations. `DELETE /products/_doc/1` removes one
document by ID, `_delete_by_query` removes everything matching a condition,
and `DELETE /products` removes the entire index along with all its documents
and its mappings. Be careful with the last form: dropping the index is
instant and there is no recycle bin.

---

## Method 2: curl (Command Line)

With curl you see the HTTP request in full: the method (`-X PUT`), the URL,
the `Content-Type` header, and the JSON body. This is exactly what Kibana
Dev Tools was sending for you. The `Content-Type: application/json` header
is not optional; Elasticsearch rejects a body without it. Working at this
level is valuable because it makes the API tangible and because curl is
available everywhere, which makes it perfect for shell scripts and pipelines.

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
