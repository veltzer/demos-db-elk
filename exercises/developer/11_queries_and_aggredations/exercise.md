# Queries and Aggregations Exercise

## Understanding Queries vs Aggregations

**Queries** answer: "Which documents match my criteria?" They return actual
documents.

**Aggregations** answer: "What patterns exist in my data?" They return
statistics, counts, averages, and grouped data.

Think of it like a library:

- **Query**: "Show me all books by Stephen King" (returns actual books)
- **Aggregation**: "How many books do we have per author?" (returns
  counts/statistics)

**Why this distinction matters:** under the hood, Elasticsearch handles
these two jobs with different machinery. A query runs against the
inverted index to find matching documents quickly, then scores and
returns them. An aggregation scans the matching documents and computes
summaries over their field values, usually reading from a column-oriented
structure called doc values. The same `_search` request can do both at
once: the `query` decides which documents participate, and the `aggs`
then summarize only those documents. Keeping this split clear in your
head is the key to writing efficient requests.

---

## Simple Exercise: Online Store Orders

Let's use a small dataset of online store orders to explore different queries
and aggregations.

### Step 1: Create Index and Add Sample Data

Before searching, we create the index with an explicit mapping. The
mapping is the schema that tells Elasticsearch the type of each field,
and that choice changes how the field can be queried later. Notice the
two text-like types used here: `customer`, `category`, and `status` are
`keyword`, while `product` is `text`. A `keyword` field is stored as a
single exact token, so it is ideal for filtering, sorting, and grouping
(`Electronics` matches only `Electronics`). A `text` field is run
through an analyzer that lowercases and splits it into terms, which makes
it good for full-text search but unsuitable for exact matching or
aggregations. Numbers (`price`, `quantity`) and the `date` field get
proper numeric and date types so that range comparisons and math work as
expected.

**Why this matters:** if you let Elasticsearch guess the mapping by
indexing data first, it would make every string both a `text` field and
a `keyword` sub-field, and it could misread your dates as plain strings.
Defining the mapping up front gives you predictable query behavior.

See [`01_create_orders_index.sh`](./01_create_orders_index.sh)

#### Add 10 Simple Orders

Each document is a single order posted to `orders/_doc/<id>`. We supply
the id ourselves (1 through 10) so the documents are easy to find and
re-run without creating duplicates. The fields line up with the mapping
above, giving us a small but varied dataset: several customers, four
categories, a spread of prices, and a few order statuses. That variety
is what makes the grouping and statistics later actually interesting.

See [`02_add_sample_orders.sh`](./02_add_sample_orders.sh)

### Step 2: Basic Queries (Finding Documents)

This step is about the `query` half of a search. Every query returns a
list of matching documents under `hits`, and `match_all` is the simplest
one: it matches every document, which is a handy way to confirm your data
loaded and to see the shape of a result.

#### 1. Find all orders (match_all)

See [`03_match_all_orders.sh`](./03_match_all_orders.sh)

**Now try these queries yourself:**

As you write these, keep one rule in mind: use `term` for exact matches
on `keyword`, numeric, or date fields (customer, category, status,
price), and use full-text style queries for the analyzed `product`
field. A common pitfall is running a `term` query against a `text` field
and getting no results, because the indexed terms are lowercased while
your `term` value is not analyzed at all. The customer, category, and
status searches below use `term`; the price search uses `range`; and the
"phone" search uses `wildcard` precisely because `product` is text.

1. Find orders by specific customer (Alice)
1. Find orders for Electronics products
1. Find orders with price greater than $50
1. Find pending orders
1. Search products containing "phone" (text search)

### Step 3: Basic Aggregations (Analyzing Data)

Now we switch to the `aggs` half. There are two broad families of
aggregations to recognize. **Bucket** aggregations group documents into
buckets, like `terms` (one bucket per distinct value) and `range` (one
bucket per numeric span). **Metric** aggregations compute a single number
over a set of documents, like `avg`, `sum`, `min`, `max`, and `stats`.
Almost everything you build is a combination of these two ideas.

Notice that the aggregation requests set `size: 0`. That tells
Elasticsearch to skip returning any actual documents and send back only
the `aggregations` section. It saves work and bandwidth when you only
care about the summary, which is the usual case for analytics.

#### 1. Count orders by category

The `terms` aggregation on the `category` keyword field produces one
bucket per category, each with a `doc_count`. This works cleanly because
`category` is a `keyword`: its exact values are the natural bucket keys.
Trying the same on a `text` field would either fail or bucket on
individual analyzed terms, which is rarely what you want.

See [`04_count_orders_by_category.sh`](./04_count_orders_by_category.sh)

**Now try these aggregations yourself:**

Try `avg` and `sum` for single-number answers, and `stats` when you want
min, max, average, sum, and count all at once from a single pass over the
data.

1. Count orders by customer
1. Calculate average order price
1. Get total sales (sum of all prices)
1. Get price statistics (min, max, avg, sum)
1. Count orders by status

### Step 4: Combined Queries and Aggregations

This is where the two halves come together, and it is the most important
concept in the exercise. When a request has both a `query` and an `aggs`
section, the aggregation runs **only over the documents the query
matched**. The query acts as a filter that narrows the population, and
the aggregation then summarizes that narrowed set. So "average price of
Electronics orders" is just a `term` query on category plus an `avg`
metric, computed together in one round trip.

Note that these combined examples leave `size` at its default, so you
will also see the matching documents in `hits` alongside the
`aggregations`. Add `size: 0` if you only want the summary.

**Try these examples that combine filtering with analysis:**

1. Find Electronics orders AND get their average price
1. Get Alice's orders AND count them by category

### Step 5: Advanced Aggregations

The real power of aggregations comes from **nesting**: placing a metric
aggregation inside a bucket aggregation. "Average price per category"
first buckets documents by category with `terms`, then computes an `avg`
of `price` inside each bucket. Elasticsearch evaluates these as a tree,
so each sub-aggregation sees only the documents that fell into its parent
bucket. You can nest several levels deep, which is how you express
questions like "for each customer, the total they spent" in one request.

The "price ranges" example uses a `range` bucket aggregation instead of
`terms`. You define the boundaries yourself, and each document lands in
exactly one bucket based on its price. Range buckets follow a
half-open convention: `from` is inclusive and `to` is exclusive, so a
price of exactly 50 falls into the `from: 50` bucket, not the `to: 50`
one. This avoids double-counting items that sit on a boundary.

**Try these more complex aggregations:**

1. Average price per category
1. Total sales per customer
1. Price ranges (buckets)

### Step 6: Understanding the Results

Knowing where to look in the response is half the battle. A `_search`
reply has two regions you care about: `hits`, produced by the query, and
`aggregations`, produced by the `aggs`. Reading the right region for the
right question keeps you from being confused by a response that contains
both.

**Query Results Include:**

- `hits.total.value`: How many documents matched
- `hits.hits[]`: The actual documents found
- `took`: How long the query took (milliseconds)

**Aggregation Results Include:**

- `aggregations`: The statistics and groupings you requested
- `buckets[]`: For grouping aggregations (terms, range)
- `value`: For metric aggregations (avg, sum, stats)

### Exercise Questions

These questions ask you to pick the right tool for each job. A useful
habit: read the question, decide whether it wants documents (a query) or
a summary (an aggregation) or both, and only then start writing. For the
"most expensive order" question, you have two valid approaches: a `max`
metric aggregation gives you just the number, while sorting the query by
price descending and taking the top hit gives you the whole document.

Try to solve these before looking at the answers below:

1. **Query**: How would you find all orders over $100?
1. **Query**: How would you find all delivered orders by Bob?
1. **Aggregation**: How would you find the most expensive order?
1. **Aggregation**: Which customer has spent the most money? (Hint: look at the
   "Total sales per customer" aggregation results above)
1. **Combined**: What's the average price of pending orders?
1. **Challenge**: Find all Electronics orders under $200 and calculate their
   total sales

### Key Takeaways

- **Queries** filter and find documents (`query` section)
- **Aggregations** analyze and summarize data (`aggs` section)
- **Combined** queries + aggregations give you filtered analysis
- **size: 0** means "don't return documents, just aggregations"
- **Nested aggregations** let you drill down (e.g., avg price per category)

### Clean Up

Deleting the index removes both the documents and the mapping, returning
your cluster to a clean state so you can re-run the exercise from
scratch. This is safe here because the data is sample data; never delete
an index you cannot recreate.

```bash
curl -X DELETE "localhost:9200/orders?pretty"
```

---

## Open-Ended Challenge

**Your Turn!** Now that you understand queries and aggregations, try to answer
these business questions using the order data. Think about what aggregations
you might need:

1. **Which category generates the most revenue?**
1. **What's the average order value per customer?**
1. **How many items (total quantity) have been ordered across all orders?**
1. **What percentage of orders are in each status?**
1. **Which price range ($0-25, $25-100, $100+) has the most orders?**

Most of these map onto patterns you have already seen. "Most revenue per
category" is a `terms` bucket with a nested `sum`, then read the largest
bucket. "Average order value per customer" is a `terms` bucket with a
nested `avg`. "Total quantity ordered" is a single `sum` over the
`quantity` field. "Percentage per status" starts from a `terms` count by
status, with the percentage worked out from the total. The price-range
question is the `range` bucket aggregation again. Recognizing that new
business questions reduce to a handful of familiar building blocks is the
skill this section is training.

Try to write the queries yourself before looking at the answers document!

### Experiment and Learn

Try creating your own aggregations:

- Change the field being analyzed
- Add or remove metrics
- Combine different aggregation types
- Filter the data differently

The best way to learn Elasticsearch is to experiment with real data and real
questions!
