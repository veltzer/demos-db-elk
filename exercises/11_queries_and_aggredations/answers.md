# Elasticsearch Queries and Aggregations - Exercise Answers

## Step 2: Basic Queries

**2. Find orders by specific customer (Alice):**

See [`11_queries_and_aggredations_05.sh`](./11_queries_and_aggredations_05.sh)


**3. Find orders for Electronics products:**

See [`11_queries_and_aggredations_06.sh`](./11_queries_and_aggredations_06.sh)


**4. Find orders with price greater than $50:**

See [`11_queries_and_aggredations_07.sh`](./11_queries_and_aggredations_07.sh)


**5. Find pending orders:**

See [`11_queries_and_aggredations_08.sh`](./11_queries_and_aggredations_08.sh)


**6. Search products containing "phone" (text search):**
See [`11_queries_and_aggredations_09.sh`](./11_queries_and_aggredations_09.sh)


## Step 3: Basic Aggregations

**2. Count orders by customer:**

See [`11_queries_and_aggredations_10.sh`](./11_queries_and_aggredations_10.sh)


**3. Calculate average order price:**

See [`11_queries_and_aggredations_11.sh`](./11_queries_and_aggredations_11.sh)


**4. Get total sales (sum of all prices):**

See [`11_queries_and_aggredations_12.sh`](./11_queries_and_aggredations_12.sh)


**5. Get price statistics (min, max, avg, sum):**

See [`11_queries_and_aggredations_13.sh`](./11_queries_and_aggredations_13.sh)


**6. Count orders by status:**

See [`11_queries_and_aggredations_14.sh`](./11_queries_and_aggredations_14.sh)


## Step 4: Combined Queries and Aggregations

**1. Find Electronics orders AND get their average price:**

See [`11_queries_and_aggredations_15.sh`](./11_queries_and_aggredations_15.sh)


**2. Get Alice orders AND count them by category:**

See [`11_queries_and_aggredations_16.sh`](./11_queries_and_aggredations_16.sh)


## Step 5: Advanced Aggregations

**1. Average price per category:**

See [`11_queries_and_aggredations_17.sh`](./11_queries_and_aggredations_17.sh)


**2. Total sales per customer:**

See [`11_queries_and_aggredations_18.sh`](./11_queries_and_aggredations_18.sh)


**3. Price ranges (buckets):**

See [`11_queries_and_aggredations_19.sh`](./11_queries_and_aggredations_19.sh)


## Basic Exercise Answers

**1. Orders over $100:**

See [`11_queries_and_aggredations_20.sh`](./11_queries_and_aggredations_20.sh)


**2. Delivered orders by Bob:**

See [`11_queries_and_aggredations_21.sh`](./11_queries_and_aggredations_21.sh)


**3. Most expensive order:**

See [`11_queries_and_aggredations_22.sh`](./11_queries_and_aggredations_22.sh)


**4. Customer who spent the most:**
Run the "Total sales per customer" aggregation from Step 5 above and look at the results. Alice spent the most with $1625.97 total.

**5. Average price of pending orders:**

See [`11_queries_and_aggredations_23.sh`](./11_queries_and_aggredations_23.sh)


**6. Challenge - Electronics orders under $200 with total sales:**

See [`11_queries_and_aggredations_24.sh`](./11_queries_and_aggredations_24.sh)


---

## Open-Ended Challenge Answers

**1. Which category generates the most revenue?**

See [`11_queries_and_aggredations_25.sh`](./11_queries_and_aggredations_25.sh)


**2. What's the average order value per customer?**

See [`11_queries_and_aggredations_26.sh`](./11_queries_and_aggredations_26.sh)


**3. How many items (total quantity) have been ordered across all orders?**

See [`11_queries_and_aggredations_27.sh`](./11_queries_and_aggredations_27.sh)


**4. What percentage of orders are in each status?**

See [`11_queries_and_aggredations_28.sh`](./11_queries_and_aggredations_28.sh)

*Note: To get percentages, you'd need to calculate them from the doc_count values returned by this aggregation.*

**5. Which price range ($0-25, $25-100, $100+) has the most orders?**

See [`11_queries_and_aggredations_29.sh`](./11_queries_and_aggredations_29.sh)


---

## Additional Sample Aggregations

**1. Total quantity of items sold:**

See [`11_queries_and_aggredations_30.sh`](./11_queries_and_aggredations_30.sh)


**2. Top 3 customers by total spending:**

See [`11_queries_and_aggredations_31.sh`](./11_queries_and_aggredations_31.sh)


**3. Date histogram - orders per day:**

See [`11_queries_and_aggredations_32.sh`](./11_queries_and_aggredations_32.sh)


**4. Extended price statistics with percentiles:**

See [`11_queries_and_aggredations_33.sh`](./11_queries_and_aggredations_33.sh)
