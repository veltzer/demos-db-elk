# Queries and Aggregations Exercise

## Understanding Queries vs Aggregations

**Queries** answer: "Which documents match my criteria?" They return actual documents.

**Aggregations** answer: "What patterns exist in my data?" They return statistics, counts, averages, and grouped data.

Think of it like a library:
- **Query**: "Show me all books by Stephen King" (returns actual books)
- **Aggregation**: "How many books do we have per author?" (returns counts/statistics)

---

## Simple Exercise: Online Store Orders

Let's use a small dataset of online store orders to explore different queries and aggregations.

### Step 1: Create Index and Add Sample Data

```bash
curl -X PUT "localhost:9200/orders?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "customer": { "type": "keyword" },
      "product": { "type": "text" },
      "category": { "type": "keyword" },
      "price": { "type": "float" },
      "quantity": { "type": "integer" },
      "date": { "type": "date" },
      "status": { "type": "keyword" }
    }
  }
}'
```

**Add 10 Simple Orders:**
```bash
curl -X POST "localhost:9200/orders/_doc/1?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Alice", "product": "Laptop", "category": "Electronics", "price": 999.99, "quantity": 1, "date": "2024-01-15", "status": "shipped" }'

curl -X POST "localhost:9200/orders/_doc/2?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Bob", "product": "Coffee Mug", "category": "Kitchen", "price": 12.50, "quantity": 2, "date": "2024-01-16", "status": "delivered" }'

curl -X POST "localhost:9200/orders/_doc/3?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Alice", "product": "Wireless Mouse", "category": "Electronics", "price": 25.99, "quantity": 1, "date": "2024-01-17", "status": "delivered" }'

curl -X POST "localhost:9200/orders/_doc/4?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Charlie", "product": "Running Shoes", "category": "Sports", "price": 89.99, "quantity": 1, "date": "2024-01-18", "status": "pending" }'

curl -X POST "localhost:9200/orders/_doc/5?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Bob", "product": "Yoga Mat", "category": "Sports", "price": 35.00, "quantity": 1, "date": "2024-01-19", "status": "shipped" }'

curl -X POST "localhost:9200/orders/_doc/6?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Alice", "product": "Smartphone", "category": "Electronics", "price": 599.99, "quantity": 1, "date": "2024-01-20", "status": "delivered" }'

curl -X POST "localhost:9200/orders/_doc/7?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Diana", "product": "Cooking Pan", "category": "Kitchen", "price": 45.99, "quantity": 1, "date": "2024-01-21", "status": "shipped" }'

curl -X POST "localhost:9200/orders/_doc/8?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Charlie", "product": "Headphones", "category": "Electronics", "price": 150.00, "quantity": 1, "date": "2024-01-22", "status": "delivered" }'

curl -X POST "localhost:9200/orders/_doc/9?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Bob", "product": "Water Bottle", "category": "Sports", "price": 18.99, "quantity": 3, "date": "2024-01-23", "status": "pending" }'

curl -X POST "localhost:9200/orders/_doc/10?pretty" -H 'Content-Type: application/json' -d'
{ "customer": "Diana", "product": "Blender", "category": "Kitchen", "price": 79.99, "quantity": 1, "date": "2024-01-24", "status": "delivered" }'
```

### Step 2: Basic Queries (Finding Documents)

**1. Find all orders (match_all):**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match_all": {}
  }
}'
```

**Now try these queries yourself:**

2. Find orders by specific customer (Alice)
3. Find orders for Electronics products
4. Find orders with price greater than $50
5. Find pending orders
6. Search products containing "phone" (text search)

### Step 3: Basic Aggregations (Analyzing Data)

**1. Count orders by category:**
```bash
curl -X GET "localhost:9200/orders/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "categories": {
      "terms": {
        "field": "category"
      }
    }
  }
}'
```

**Now try these aggregations yourself:**

2. Count orders by customer
3. Calculate average order price
4. Get total sales (sum of all prices)
5. Get price statistics (min, max, avg, sum)
6. Count orders by status

### Step 4: Combined Queries and Aggregations

**Try these examples that combine filtering with analysis:**

1. Find Electronics orders AND get their average price
2. Get Alice's orders AND count them by category

### Step 5: Advanced Aggregations

**Try these more complex aggregations:**

1. Average price per category
2. Total sales per customer
3. Price ranges (buckets)

### Step 6: Understanding the Results

**Query Results Include:**
- `hits.total.value`: How many documents matched
- `hits.hits[]`: The actual documents found
- `took`: How long the query took (milliseconds)

**Aggregation Results Include:**
- `aggregations`: The statistics and groupings you requested
- `buckets[]`: For grouping aggregations (terms, range)
- `value`: For metric aggregations (avg, sum, stats)

### Exercise Questions

Try to solve these before looking at the answers below:

1. **Query**: How would you find all orders over $100?
2. **Query**: How would you find all delivered orders by Bob?
3. **Aggregation**: How would you find the most expensive order?
4. **Aggregation**: Which customer has spent the most money? (Hint: look at the "Total sales per customer" aggregation results above)
5. **Combined**: What's the average price of pending orders?
6. **Challenge**: Find all Electronics orders under $200 and calculate their total sales

### Key Takeaways

- **Queries** filter and find documents (`query` section)
- **Aggregations** analyze and summarize data (`aggs` section)
- **Combined** queries + aggregations give you filtered analysis
- **size: 0** means "don't return documents, just aggregations"
- **Nested aggregations** let you drill down (e.g., avg price per category)

### Clean Up

```bash
curl -X DELETE "localhost:9200/orders?pretty"
```

---

## Open-Ended Challenge

**Your Turn!** Now that you understand queries and aggregations, try to answer these business questions using the order data. Think about what aggregations you might need:

1. **Which category generates the most revenue?**
2. **What's the average order value per customer?**
3. **How many items (total quantity) have been ordered across all orders?**
4. **What percentage of orders are in each status?**
5. **Which price range ($0-25, $25-100, $100+) has the most orders?**

Try to write the queries yourself before looking at the answers document!

### Experiment and Learn!

Try creating your own aggregations:
- Change the field being analyzed
- Add or remove metrics
- Combine different aggregation types
- Filter the data differently

The best way to learn Elasticsearch is to experiment with real data and real questions!
