# Query Performance and Indexing in Elasticsearch

## Objective

Learn how to measure Elasticsearch query performance and understand the impact
of field indexing on query speed.

When you store a document in Elasticsearch, each field can be treated very
differently behind the scenes. By default, Elasticsearch builds an *inverted
index* for every field: a data structure that maps each term back to the
documents that contain it, much like the index at the back of a textbook. That
inverted index is what makes searches fast, but it also costs disk space,
memory, and time to build during indexing. The central idea of this exercise is
that you do not always need to pay that cost. Some fields are only ever shown to
the user and never searched, and for those you can turn indexing off with
`index: false`. The exercises below let you measure the trade-off for yourself
rather than just take it on faith.

## Prerequisites

- Python 3.x with modules: `elasticsearch`, `faker`
- Elasticsearch running on <http://localhost:9200>
- Install required modules:

```bash
pip install elasticsearch faker
```

## Part 1: Generate Test Data

First, create test data using the provided script:

See [`01_generate_test_data.sh`](./01_generate_test_data.sh)

This creates two indices:

- `users_indexed`: All fields are indexed (searchable)
- `users_non_indexed`: Some fields have `index: false` (stored but not searchable)

**Why two indices?** To compare fairly you need two populations that differ in
exactly one variable: whether certain fields are indexed. The script defines two
*mappings* (the schema that tells Elasticsearch the type of each field) and
fills both indices with the same kind of randomly generated user data. The only
difference is that in `users_non_indexed` fields such as `email`, `bio`,
`salary`, `job_title`, `last_login`, `metadata`, and several `location`
sub-fields are marked `index: false`.

**What's happening under the hood:** the data is loaded with the *bulk* API,
which sends many documents in a single request instead of one HTTP call per
document. This is the standard way to index at scale because per-request
overhead dominates when you index one document at a time. After loading, the
script calls
a *refresh* on each index. Newly indexed documents are not visible to search
until a refresh flushes them from the in-memory buffer into a searchable
*segment*; refreshing explicitly guarantees the test queries can find the data
immediately.

**Concept: keyword vs text.** Notice in the mapping that some fields are
`keyword` (stored as a single exact token, good for filters, sorting, and
aggregations) while others are `text` (broken into individual words by an
*analyzer* so you can do full-text `match` queries). The same raw string is
indexed very differently depending on which type you choose, and that choice
drives which queries are even possible.

## Part 2: Query Performance Measurement

Measuring query speed sounds simple but is easy to get wrong. Two ideas run
through every script in this part. First, you should run the same query several
times and look at the average, minimum, and maximum, because the first run is
often slower than later runs: Elasticsearch and the operating system *cache*
data on the first access, so repeated queries hit warm caches and run faster.
Second, there are two clocks to be aware of. The client-side timer measures the
full round trip including network and Python overhead, while the `took` value
that Elasticsearch returns measures only the time spent inside the cluster. When
they diverge, the gap is overhead outside Elasticsearch itself.

### Exercise 2.1: Basic Query Timing

See [`02_basic_query_timing.py`](./02_basic_query_timing.py)

**What this teaches:** it runs a `term` query on the indexed `department` field
and times five runs. A `term` query asks for an exact match against an indexed
value and does no analysis, so it is about as fast as Elasticsearch gets. This
establishes a baseline you can compare everything else against. Watch how the
first run is typically slower than the rest as the caches warm up.

### Exercise 2.2: Compare Indexed vs Non-Indexed Fields

See [`03_compare_indexed_vs_non_indexed.py`](./03_compare_indexed_vs_non_indexed.py)

**What this teaches:** it runs the same queries against both indices and reports
the difference. The key lesson is not that non-indexed fields are *slow* to
search, it is that they cannot be searched at all. A query against a field with
`index: false` raises an error, and the script catches that error and prints it.
This is why the script first reads one real document and reuses its actual field
values: a `term` query only matches when the value truly exists, so using a
sampled value avoids the trap of "zero hits" that looks like a bug but is really
just a value that was never in the data.

### Exercise 2.3: Using Elasticsearch's Profile API

See [`04_profile_api.py`](./04_profile_api.py)

**What this teaches:** the Profile API turns on detailed instrumentation by
adding `"profile": true` to the request. Instead of a single timing number, you
get a per-shard breakdown of how long each part of the query took, in
nanoseconds. This matters because an index is split into *shards* (independent
sub-indices that run in parallel), and a query runs on each shard separately.
The script profiles a `bool` query that combines `must`, `should`, and a range
filter, so you can see which clause dominates the cost. Use the Profile API when
a query is unexpectedly slow and you need to know *why* rather than just *how
slow*.

### Exercise 2.4: Aggregation Performance

See [`05_aggregation_performance.py`](./05_aggregation_performance.py)

**What this teaches:** *aggregations* summarize data into buckets and metrics
(for example, how many users are in each department) rather than returning
individual documents, which is why the script sets `size: 0` to skip returning
hits. The important concept here is that aggregations rely on *doc values*, a
columnar, on-disk structure that Elasticsearch builds only for indexed fields. A
field marked `index: false` has no doc values, so trying to aggregate on it
fails just like searching it does. The script demonstrates this by aggregating
on the indexed `department` field (success) and the non-indexed `email` field
(error).

### Exercise 2.5: Scroll Performance for Large Result Sets

See [`06_scroll_performance.py`](./06_scroll_performance.py)

**What this teaches:** a normal search returns only the first page of results,
and asking for very deep pages is expensive. The *scroll* API solves this by
taking a consistent snapshot of the index and letting you walk through all
matching documents in batches. The script keeps a `scroll` context alive for two
minutes, pulls 1000 documents per batch, and clears the context when done.
Clearing matters: each open scroll holds resources on the server, so leaving
them open wastes memory. The script reports throughput in documents per second,
which is the right metric for bulk export rather than single-query latency.

**Pitfall:** scroll is meant for processing large result sets in the background,
not for real-time user-facing pagination. For interactive paging, prefer
`search_after`.

## Part 3: Advanced Performance Testing

### Exercise 3.1: Concurrent Query Performance

See [`07_concurrent_query_performance.py`](./07_concurrent_query_performance.py)

**What this teaches:** a single query timed in isolation tells you nothing about
how the system behaves under load. Real clusters serve many users at once, and
throughput and latency change as concurrency rises. The script fires many
queries from several threads at the same time and reports averages along with
the *median* and the *95th percentile* (the value below which 95 percent of
queries
fall). Percentiles matter more than averages for user experience: a low average
can still hide a slow tail that frustrates a minority of users. Throughput in
queries per second tells you how much work the cluster can absorb before it
saturates.

### Exercise 3.2: Script to Demonstrate Non-Indexed Field Impact

See [`08_demonstrate_non_indexed_impact.py`](./08_demonstrate_non_indexed_impact.py)

**What this teaches:** this is the capstone for Part 2 and Part 3. It runs a
table of test cases across `term`, `range`, and `match` query types against both
indices and prints a summary table. The recurring pattern in the output is
"Cannot Query" for the non-indexed fields, which drives home the main point: the
real cost of `index: false` is not slower search, it is *no search at all*. The
field is still stored and still returned in results, you simply cannot filter,
sort, or aggregate on it.

## Part 4: Best Practices and Optimization

Knowing *how* to disable indexing is only half the skill. The harder, more
valuable half is deciding *which* fields should give up their index. The rule of
thumb is simple: index a field only if you will search, filter, sort, or
aggregate on it. Everything else is a candidate for `index: false`. The payoff
is real: a smaller index, faster indexing of new documents, less memory
pressure,
and lighter cluster-state and disk activity.

### Exercise 4.1: Identify Fields to Not Index

See [`09_identify_fields_to_not_index.py`](./09_identify_fields_to_not_index.py)

**What this teaches:** unlike the earlier scripts, this one does not call
Elasticsearch at all. It prints a decision guide that sorts the example user
fields into "keep indexed", "consider disabling", and "definitely disable", then
lists the concrete benefits of disabling. Treat it as a checklist for reviewing
a mapping. The judgment it encodes is exactly what you will be asked to apply in
the challenge exercises below.

## Summary and Key Takeaways

1. **Non-indexed fields cannot be searched** - Queries will fail with an error
1. **Non-indexed fields can still be retrieved** - They appear in search results
1. **Performance impact** - Indexed fields enable fast searches; without
   indexing, fields cannot be queried at all
1. **Use cases for `index: false`**:
   - Display-only fields
   - Large text fields not used for search
   - Binary/encoded data
   - Internal tracking fields

1. **Best practices**:
   - Analyze field usage before deciding on indexing
   - Use `index: false` for fields that are never searched
   - Consider storage vs query requirements
   - Monitor index size and performance

## Challenge Exercises

1. **Create a hybrid mapping** where commonly searched fields are indexed and
   rarely used fields are not
1. **Measure index size difference** between fully indexed and partially indexed
   indices
1. **Test update performance** when updating indexed vs non-indexed fields
1. **Design a mapping strategy** for a real-world application optimizing for both
   storage and query performance
