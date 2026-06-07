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

See [`11_queries_and_aggredations_01.sh`](./11_queries_and_aggredations_01.sh)


**Add 10 Simple Orders:**
See [`11_queries_and_aggredations_02.sh`](./11_queries_and_aggredations_02.sh)


### Step 2: Basic Queries (Finding Documents)

**1. Find all orders (match_all):**
See [`11_queries_and_aggredations_03.sh`](./11_queries_and_aggredations_03.sh)


**Now try these queries yourself:**

2. Find orders by specific customer (Alice)
3. Find orders for Electronics products
4. Find orders with price greater than $50
5. Find pending orders
6. Search products containing "phone" (text search)

### Step 3: Basic Aggregations (Analyzing Data)

**1. Count orders by category:**
See [`11_queries_and_aggredations_04.sh`](./11_queries_and_aggredations_04.sh)


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
