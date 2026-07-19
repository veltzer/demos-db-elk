# ES|QL Exercise

## Understanding ES|QL

**ES|QL** (Elasticsearch Query Language) is a piped query language for
Elasticsearch. Instead of building a nested JSON request out of `query`
and `aggs` sections, you write a single line of text: a **source command**
that names the data (`FROM orders`), followed by **processing commands**
chained with the pipe character (`|`). Each command receives a table of
rows, transforms it, and hands the result to the next command — exactly
like piping in a Unix shell:

```text
FROM orders | WHERE price > 50 | SORT price DESC | LIMIT 3
```

If you did the
[queries and aggregations exercise](../06_queries_and_aggregations/exercise.md),
you already know
the two jobs a search request performs: *finding* documents and
*summarizing* them. ES|QL covers both jobs with one uniform pipeline:
`WHERE` plays the role of the `query` section, and `STATS ... BY` plays
the role of the `aggs` section. In this exercise we deliberately reuse
the same orders dataset and re-answer the same business questions, so
you can compare the two languages side by side and see that they are two
ways of asking the same engine the same questions.

**Why learn both?** The Query DSL remains the native language of search:
relevance scoring, full-text matching, and every corner feature live
there first. ES|QL shines for the analyst-style workflow — filter,
compute, group, sort — where its one-line pipelines are far easier to
read, write, and iterate on than deeply nested JSON. It also computes
new columns on the fly (`EVAL`), something the Query DSL only reaches
via scripting. ES|QL ships with Elasticsearch since 8.11, so the 9.x
cluster from the install exercise supports it out of the box.

---

## Simple Exercise: Online Store Orders, Revisited

We reuse the online store orders dataset from the
[queries and aggregations exercise](../06_queries_and_aggregations/exercise.md):
same mapping, same ten documents.

### Step 1: Create Index and Add Sample Data

The mapping matters to ES|QL just as it does to the Query DSL. The
`keyword` fields (`customer`, `category`, `status`) hold exact values,
which is what makes equality comparisons like `customer == "Alice"`
work naturally. The `text` field (`product`) is analyzed for full-text
search; ES|QL can still read and filter it, but as you will see below it
compares the *original* value, not the lowercased analyzed terms.

See [`01_create_orders_index.sh`](./01_create_orders_index.sh)

Load the ten orders. Note the extra `_refresh` call at the end: newly
indexed documents only become visible to queries after a refresh, and
since we run our first ES|QL query immediately, we force one instead of
waiting for the automatic refresh interval.

See [`02_add_sample_orders.sh`](./02_add_sample_orders.sh)

### Step 2: Your First ES|QL Query

ES|QL queries are sent to the `_query` endpoint. The whole pipeline is a
single string in the `query` field of the request body. Note that the
endpoint is not tied to an index in the URL — the pipeline itself says
where the data comes from, with `FROM orders`.

Two things to notice in the script. First, `FROM orders | LIMIT 10` is
the ES|QL equivalent of `match_all`: take the `orders` index, keep at
most 10 rows. Second, the URL parameter `format=txt` asks Elasticsearch
to render the result as an aligned text table, which is by far the most
readable format while learning. Other formats include `csv` and the
default JSON.

See [`03_first_esql_query.sh`](./03_first_esql_query.sh)

Run the same query without `format=txt` to see the default JSON
response. Where a `_search` response has `hits`, an ES|QL response has
`columns` (name and type of each output column) and `values` (one array
per row). This columnar shape is what programs consume; the `txt` table
is the same data rendered for humans.

See [`04_json_response.sh`](./04_json_response.sh)

**A word about LIMIT:** if a pipeline contains no `LIMIT`, Elasticsearch
applies a default cap of 1000 rows (and it will never return more than
10000). With our ten documents that never bites, but on real data it
means an ES|QL query without `LIMIT` is not necessarily giving you
everything — get in the habit of stating the limit you mean.

### Step 3: Filtering and Shaping — WHERE, KEEP, SORT

`WHERE` keeps only the rows that satisfy a condition; it is the pipeline
counterpart of the `query` section. Comparisons use familiar operators:
`==` for equality (note: double equals, not single), `>` and `<` for
ranges, and boolean combinations with `AND`, `OR`, and `NOT`.

See [`05_where_price_over_50.sh`](./05_where_price_over_50.sh) — orders
with price greater than $50, the same question answered with a `range`
query in the previous exercise.

A `_search` returns whole documents; an ES|QL pipeline returns a table
whose columns you control. `KEEP` selects (and orders) the columns you
want, and `SORT` orders the rows. Because every command feeds the next,
you can read the pipeline aloud: "take orders, keep these three columns,
sort by price descending."

See [`06_keep_and_sort.sh`](./06_keep_and_sort.sh)

**Now try these yourself:**

Remember the type rule from the mapping: `customer`, `category`, and
`status` are `keyword` fields, so exact `==` comparisons work on them.
The `product` field is `text`; ES|QL compares its original value, so a
pattern match with `LIKE` is case-sensitive. `LIKE` uses shell-style
wildcards (`*` for any run of characters), and wrapping the field in
`TO_LOWER(...)` makes the match case-insensitive — that is the trick for
finding "phone" inside both "Smartphone" and "Headphones".

1. Find orders by specific customer (Alice)
1. Find pending orders, showing only customer, product, price and status
1. Find Electronics orders sorted by price, most expensive first
1. Find products containing "phone" (use `TO_LOWER` and `LIKE`)

### Step 4: Computing New Columns — EVAL

`EVAL` adds a new column computed from existing ones. This is something
the Query DSL cannot do without scripting: our documents store `price`
and `quantity`, but the business cares about the line total, and `EVAL
line_total = price * quantity` materializes it as a real column that
every later command can filter on, sort by, or aggregate.

See [`07_eval_line_total.sh`](./07_eval_line_total.sh)

Look at Bob's Water Bottle row in the output: 3 bottles at $18.99 make a
line total of $56.97 — a number that exists in no document. From here on
we use `line_total` whenever a question asks about revenue, because
summing `price` alone would short-change multi-item orders.

### Step 5: Summarizing — STATS ... BY

`STATS` is the aggregation command. On its own it collapses the whole
table to a single row of metrics; with `BY` it groups rows first and
computes the metrics per group — the counterpart of a `terms` bucket
aggregation with nested metrics. The metric functions have familiar
names: `COUNT(*)`, `AVG`, `SUM`, `MIN`, `MAX`.

See [`08_stats_count_by_category.sh`](./08_stats_count_by_category.sh) —
one row per category with its order count, the same answer the `terms`
aggregation gave us, without any `size: 0` tricks: an ES|QL result *is*
just the table you asked for.

**Now try these yourself:**

For the revenue question, chain what you learned: `EVAL` the line total
first, then `SUM` it in `STATS`. `ROUND(value, 2)` tidies up floating
point noise in averages.

1. Calculate the average order price
1. Calculate total revenue (hint: `EVAL` line totals, then `SUM` them)
1. Count orders by status, most common status first
1. For each category: order count, min, max and average price, sorted by
   average price

### Step 6: Putting It Together — Multi-Stage Pipelines

The payoff of the pipe model is that filtering, computing, grouping,
sorting, and limiting compose freely, in any order that makes sense.
"Average price of Electronics orders" — a query-plus-aggregation
combination in the previous exercise — is here just a `WHERE` followed
by a `STATS`. "Top 3 customers by spending" reads exactly like the
sentence: compute line totals, sum per customer, sort descending, take
three. Note that `SORT` and `LIMIT` here run *after* the aggregation,
operating on the grouped rows — something that took a special ordered
`terms` aggregation to express in the Query DSL.

**Try these yourself:**

1. Find the top 3 customers by total spending
1. Find Electronics orders and compute their count and average price
1. Show the 5 largest line totals with customer and product

### Exercise Questions

As in the previous exercise, decide first what the question needs — a
filter (`WHERE`), a computation (`EVAL`), a summary (`STATS`), or a
chain of them — then write the pipeline. Try these before peeking at the
answers document:

1. How would you find all orders over $100?
1. How would you find all delivered orders by Bob?
1. Which category generates the most revenue?
1. What is the average price of pending orders?
1. **Challenge**: find Electronics orders under $200 and calculate their
   total revenue

### Key Takeaways

- ES|QL is a **piped language**: `FROM` names the data, each `|` command
  transforms a table and passes it on
- **WHERE** filters rows (the `query` section's job); **STATS ... BY**
  groups and summarizes (the `aggs` section's job)
- **EVAL** computes new columns on the fly — no scripting required
- **KEEP**, **SORT**, and **LIMIT** shape the output table; without an
  explicit `LIMIT` results are capped at 1000 rows
- The response is **columnar** (`columns` + `values`); `format=txt`
  renders it as a readable table
- `keyword` fields compare exactly with `==`; `text` fields keep their
  original value, so use `TO_LOWER` + `LIKE` for case-insensitive
  matching

### Clean Up

As always, deleting the index returns the cluster to a clean state so
the exercise can be re-run from scratch:

```bash
curl -X DELETE "localhost:9200/orders?pretty"
```

---

## Open-Ended Challenge

**Your Turn!** Re-answer the open-ended questions from the queries and
aggregations exercise, this time in ES|QL, and compare how the two
solutions read:

1. **Which customer has the highest average order value?**
1. **How many items (total quantity) have been ordered across all
   orders?**
1. **Which price range ($0-25, $25-100, $100+) has the most orders?**
   (hint: `EVAL` a label column with `CASE(...)`, then count by it)
1. **For each status, what is the total revenue?**

The price-range question is worth the effort: where the Query DSL has a
dedicated `range` aggregation, in ES|QL you build the buckets yourself
with `CASE(price < 25, "budget", price < 100, "mid", "premium")` and
then `STATS ... BY` the label. It is a good illustration of the
trade-off between the two languages — the Query DSL gives you many
specialized aggregations, ES|QL gives you a few composable commands.

### Experiment and Learn

- Open Kibana → Discover and switch the query bar to **ES|QL** mode: the
  same pipelines you wrote with curl work there, with autocomplete and
  instant tables
- Try `DROP` (the inverse of `KEEP`), `RENAME`, and sorting by multiple
  columns
- Ask for `format=csv` and pipe the output into your favorite
  command-line tools

The best way to learn ES|QL is the pipe itself: start with `FROM orders`,
add one command at a time, and watch the table change!
