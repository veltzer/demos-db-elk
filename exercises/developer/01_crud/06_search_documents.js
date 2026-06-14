#!/usr/bin/env node
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
