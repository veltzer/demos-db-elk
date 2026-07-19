# ES|QL - Exercise Answers

## Step 3: Filtering and Shaping

**1. Find orders by specific customer (Alice):**

See [`09_alice_orders.sh`](./09_alice_orders.sh)

**2. Find pending orders, showing only customer, product, price and status:**

See [`10_pending_orders.sh`](./10_pending_orders.sh)

**3. Find Electronics orders sorted by price, most expensive first:**

See [`11_electronics_sorted_by_price.sh`](./11_electronics_sorted_by_price.sh)

**4. Find products containing "phone":**

See [`12_products_containing_phone.sh`](./12_products_containing_phone.sh)

## Step 5: Summarizing

**1. Calculate the average order price:**

See [`13_average_order_price.sh`](./13_average_order_price.sh)

**2. Calculate total revenue:**

See [`14_total_revenue.sh`](./14_total_revenue.sh)

**3. Count orders by status, most common status first:**

See [`15_count_by_status.sh`](./15_count_by_status.sh)

**4. Per-category order count, min, max and average price:**

See [`16_price_stats_by_category.sh`](./16_price_stats_by_category.sh)

## Step 6: Multi-Stage Pipelines

**1. Top 3 customers by total spending:**

See [`17_top_3_customers_by_spending.sh`](./17_top_3_customers_by_spending.sh)

**2. Electronics orders — count and average price:**

See [`18_electronics_average_price.sh`](./18_electronics_average_price.sh)

**3. The 5 largest line totals:**

See [`19_top_5_line_totals.sh`](./19_top_5_line_totals.sh)

## Exercise Question Answers

**1. All orders over $100:**

```text
FROM orders | WHERE price > 100
```

**2. All delivered orders by Bob:**

```text
FROM orders | WHERE customer == "Bob" AND status == "delivered"
```

**3. Which category generates the most revenue:**

```text
FROM orders
| EVAL line_total = price * quantity
| STATS revenue = SUM(line_total) BY category
| SORT revenue DESC
```

**4. Average price of pending orders:**

```text
FROM orders | WHERE status == "pending" | STATS avg_price = AVG(price)
```

**5. Challenge — Electronics under $200, total revenue:**

```text
FROM orders
| WHERE category == "Electronics" AND price < 200
| EVAL line_total = price * quantity
| STATS total_revenue = SUM(line_total)
```

## Open-Ended Challenge Answers

**1. Customer with the highest average order value:**

```text
FROM orders
| EVAL line_total = price * quantity
| STATS avg_order_value = ROUND(AVG(line_total), 2) BY customer
| SORT avg_order_value DESC
| LIMIT 1
```

**2. Total quantity ordered across all orders:**

```text
FROM orders | STATS total_items = SUM(quantity)
```

**3. Price range with the most orders:**

```text
FROM orders
| EVAL price_range = CASE(price < 25, "budget", price < 100, "mid", "premium")
| STATS order_count = COUNT(*) BY price_range
| SORT order_count DESC
```

**4. Total revenue per status:**

```text
FROM orders
| EVAL line_total = price * quantity
| STATS revenue = ROUND(SUM(line_total), 2) BY status
| SORT revenue DESC
```
