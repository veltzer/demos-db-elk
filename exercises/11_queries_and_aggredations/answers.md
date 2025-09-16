# Elasticsearch Queries and Aggregations - Exercise Answers

## Step 2: Basic Queries

**2. Find orders by specific customer (Alice):**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": {
      "customer": "Alice"
    }
  }
}'
```

**3. Find orders for Electronics products:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": {
      "category": "Electronics"
    }
  }
}'
```

**4. Find orders with price greater than $50:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "range": {
      "price": {
        "gt": 50
      }
    }
  }
}'
```

**5. Find pending orders:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": {
      "status": "pending"
    }
  }
}'
```

**6. Search products containing "phone" (text search):**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "product": "phone"
    }
  }
}'
```

## Step 3: Basic Aggregations

**2. Count orders by customer:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "customers": {
      "terms": {
        "field": "customer"
      }
    }
  }
}'
```

**3. Calculate average order price:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "avg_price": {
      "avg": {
        "field": "price"
      }
    }
  }
}'
```

**4. Get total sales (sum of all prices):**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "total_sales": {
      "sum": {
        "field": "price"
      }
    }
  }
}'
```

**5. Get price statistics (min, max, avg, sum):**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "price_stats": {
      "stats": {
        "field": "price"
      }
    }
  }
}'
```

**6. Count orders by status:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "order_status": {
      "terms": {
        "field": "status"
      }
    }
  }
}'
```

## Step 4: Combined Queries and Aggregations

**1. Find Electronics orders AND get their average price:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": {
      "category": "Electronics"
    }
  },
  "aggs": {
    "avg_electronics_price": {
      "avg": {
        "field": "price"
      }
    }
  }
}'
```

**2. Get Alice orders AND count them by category:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": {
      "customer": "Alice"
    }
  },
  "aggs": {
    "alice_categories": {
      "terms": {
        "field": "category"
      }
    }
  }
}'
```

## Step 5: Advanced Aggregations

**1. Average price per category:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "categories": {
      "terms": {
        "field": "category"
      },
      "aggs": {
        "avg_price": {
          "avg": {
            "field": "price"
          }
        }
      }
    }
  }
}'
```

**2. Total sales per customer:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "customers": {
      "terms": {
        "field": "customer"
      },
      "aggs": {
        "total_spent": {
          "sum": {
            "field": "price"
          }
        }
      }
    }
  }
}'
```

**3. Price ranges (buckets):**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [
          { "to": 50 },
          { "from": 50, "to": 100 },
          { "from": 100 }
        ]
      }
    }
  }
}'
```

## Basic Exercise Answers

**1. Orders over $100:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "range": {
      "price": { "gt": 100 }
    }
  }
}'
```

**2. Delivered orders by Bob:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "term": { "customer": "Bob" } },
        { "term": { "status": "delivered" } }
      ]
    }
  }
}'
```

**3. Most expensive order:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "max_price": {
      "max": { "field": "price" }
    }
  }
}'
```

**4. Customer who spent the most:**
Run the "Total sales per customer" aggregation from Step 5 above and look at the results. Alice spent the most with $1625.97 total.

**5. Average price of pending orders:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": { "status": "pending" }
  },
  "aggs": {
    "avg_pending_price": {
      "avg": { "field": "price" }
    }
  }
}'
```

**6. Challenge - Electronics orders under $200 with total sales:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "term": { "category": "Electronics" } },
        { "range": { "price": { "lt": 200 } } }
      ]
    }
  },
  "aggs": {
    "total_electronics_sales": {
      "sum": { "field": "price" }
    }
  }
}'
```

---

## Open-Ended Challenge Answers

**1. Which category generates the most revenue?**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "revenue_by_category": {
      "terms": {
        "field": "category"
      },
      "aggs": {
        "total_revenue": {
          "sum": { "field": "price" }
        }
      }
    }
  }
}'
```

**2. What's the average order value per customer?**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "avg_order_per_customer": {
      "terms": {
        "field": "customer"
      },
      "aggs": {
        "avg_order_value": {
          "avg": { "field": "price" }
        }
      }
    }
  }
}'
```

**3. How many items (total quantity) have been ordered across all orders?**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "total_items_ordered": {
      "sum": { "field": "quantity" }
    }
  }
}'
```

**4. What percentage of orders are in each status?**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "status_distribution": {
      "terms": {
        "field": "status"
      }
    }
  }
}'
```
*Note: To get percentages, you'd need to calculate them from the doc_count values returned by this aggregation.*

**5. Which price range ($0-25, $25-100, $100+) has the most orders?**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [
          { "key": "$0-25", "from": 0, "to": 25 },
          { "key": "$25-100", "from": 25, "to": 100 },
          { "key": "$100+", "from": 100 }
        ]
      }
    }
  }
}'
```

---

## Additional Sample Aggregations

**1. Total quantity of items sold:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "total_items": {
      "sum": {
        "field": "quantity"
      }
    }
  }
}'
```

**2. Top 3 customers by total spending:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "top_customers": {
      "terms": {
        "field": "customer",
        "size": 3,
        "order": {
          "total_spent": "desc"
        }
      },
      "aggs": {
        "total_spent": {
          "sum": {
            "field": "price"
          }
        }
      }
    }
  }
}'
```

**3. Date histogram - orders per day:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "orders_per_day": {
      "date_histogram": {
        "field": "date",
        "calendar_interval": "day"
      }
    }
  }
}'
```

**4. Extended price statistics with percentiles:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "price_percentiles": {
      "percentiles": {
        "field": "price",
        "percents": [25, 50, 75