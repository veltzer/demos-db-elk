# Elasticsearch Queries and Aggregations - Exercise Answers

## Step 2: Basic Queries

**2. Find orders by specific customer (Alice):**

See [`05_find_orders_by_customer_alice.sh`](./05_find_orders_by_customer_alice.sh)

**3. Find orders for Electronics products:**

See [`06_find_electronics_orders.sh`](./06_find_electronics_orders.sh)

**4. Find orders with price greater than $50:**

See [`07_find_orders_price_over_50.sh`](./07_find_orders_price_over_50.sh)

**5. Find pending orders:**

See [`08_find_pending_orders.sh`](./08_find_pending_orders.sh)

**6. Search products containing "phone" (text search):**

See [`09_search_products_containing_phone.sh`](./09_search_products_containing_phone.sh)

## Step 3: Basic Aggregations

**2. Count orders by customer:**

See [`10_count_orders_by_customer.sh`](./10_count_orders_by_customer.sh)

**3. Calculate average order price:**

See [`11_average_order_price.sh`](./11_average_order_price.sh)

**4. Get total sales (sum of all prices):**

See [`12_total_sales_sum.sh`](./12_total_sales_sum.sh)

**5. Get price statistics (min, max, avg, sum):**

See [`13_price_statistics.sh`](./13_price_statistics.sh)

**6. Count orders by status:**

See [`14_count_orders_by_status.sh`](./14_count_orders_by_status.sh)

## Step 4: Combined Queries and Aggregations

**1. Find Electronics orders AND get their average price:**

See [`15_electronics_average_price.sh`](./15_electronics_average_price.sh)

**2. Get Alice orders AND count them by category:**

See [`16_alice_orders_by_category.sh`](./16_alice_orders_by_category.sh)

## Step 5: Advanced Aggregations

**1. Average price per category:**

See [`17_average_price_per_category.sh`](./17_average_price_per_category.sh)

**2. Total sales per customer:**

See [`18_total_sales_per_customer.sh`](./18_total_sales_per_customer.sh)

**3. Price ranges (buckets):**

See [`19_price_range_buckets.sh`](./19_price_range_buckets.sh)

## Basic Exercise Answers

**1. Orders over $100:**

See [`20_orders_over_100.sh`](./20_orders_over_100.sh)

**2. Delivered orders by Bob:**

See [`21_delivered_orders_by_bob.sh`](./21_delivered_orders_by_bob.sh)

**3. Most expensive order:**

See [`22_most_expensive_order.sh`](./22_most_expensive_order.sh)

**4. Customer who spent the most:**

Run the "Total sales per customer" aggregation from Step 5 above and look at the
results. Alice spent the most with $1625.97 total.

**5. Average price of pending orders:**

See [`23_average_price_pending_orders.sh`](./23_average_price_pending_orders.sh)

**6. Challenge - Electronics orders under $200 with total sales:**

See [`24_electronics_under_200_total_sales.sh`](./24_electronics_under_200_total_sales.sh)

---

## Open-Ended Challenge Answers

**1. Which category generates the most revenue?**

See [`25_revenue_by_category.sh`](./25_revenue_by_category.sh)

**2. What's the average order value per customer?**

See [`26_average_order_value_per_customer.sh`](./26_average_order_value_per_customer.sh)

**3. How many items (total quantity) have been ordered across all orders?**

See [`27_total_items_ordered.sh`](./27_total_items_ordered.sh)

**4. What percentage of orders are in each status?**

See [`28_order_status_distribution.sh`](./28_order_status_distribution.sh)

*Note: To get percentages, you'd need to calculate them from the doc_count
values returned by this aggregation.*

**5. Which price range ($0-25, $25-100, $100+) has the most orders?**

See [`29_price_range_with_most_orders.sh`](./29_price_range_with_most_orders.sh)

---

## Additional Sample Aggregations

**1. Total quantity of items sold:**

See [`30_total_quantity_sold.sh`](./30_total_quantity_sold.sh)

**2. Top 3 customers by total spending:**

See [`31_top_3_customers_by_spending.sh`](./31_top_3_customers_by_spending.sh)

**3. Date histogram - orders per day:**

See [`32_orders_per_day_histogram.sh`](./32_orders_per_day_histogram.sh)

**4. Extended price statistics with percentiles:**

See [`33_price_percentiles.sh`](./33_price_percentiles.sh)
