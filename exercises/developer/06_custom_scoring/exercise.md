# Custom Scoring Functions with `function_score` Queries

## Objective

Learn how to implement custom scoring algorithms in Elasticsearch using
`function_score` queries to boost relevance based on business requirements.

## Background

Default Elasticsearch scoring (TF-IDF or BM25) works well for text relevance,
but often you need to incorporate business metrics like:

- Popularity, ratings, or views
- Recency or freshness
- Geographic proximity
- User preferences
- Stock levels or availability

When you run a plain `match` query, Elasticsearch computes a relevance score
(`_score`) for each document based only on the words in the text. BM25, the
default algorithm, rewards documents where the query terms are frequent in
the field but rare across the whole index. That is great for "find documents
about X" but it knows nothing about whether a product is in stock, highly
rated, or profitable. A perfectly relevant match for a discontinued, badly
reviewed item would still rank at the top.

The `function_score` query solves this by letting you take the text relevance
score and adjust it with one or more scoring functions that read your own
fields. The key idea is the two-stage pipeline: first the inner `query`
decides which documents match and gives each a base `_score`, then the
functions transform that base score using business data. Two settings control
how the pieces combine:

- `score_mode` decides how multiple functions are combined with each other
  (for example `sum`, `multiply`, `max`).
- `boost_mode` decides how the combined function result is merged with the
  original query `_score` (for example `multiply`, `sum`, `replace`).

Keeping these two stages separate in your mind is the single most important
concept in this whole exercise. Almost every confusing result comes from
mixing them up.

## Part 1: Basic Function Score

### Exercise 1.1: Setup Sample E-commerce Data

See [`01_setup_sample_products.py`](./01_setup_sample_products.py)

**Task:** Create the index and load sample data.

This script first defines an explicit mapping before indexing anything. That
matters for scoring: every field you plan to use in a function needs the right
type. Numeric fields like `rating` and `view_count` must be numbers so they
can be multiplied, `created_date` must be a `date` so decay can measure age,
and `location` must be a `geo_point` so distance can be calculated. If you let
Elasticsearch guess the mapping, a number could be detected as `text` and
your function would fail or behave oddly. The script generates 100 random
products so that later queries have a realistic spread of ratings, prices,
ages, and locations to sort between.

### Exercise 1.2: Simple Field Value Factor

See [`02_popularity_boost.py`](./02_popularity_boost.py)

**Task:** Modify to boost by rating instead of view_count.

This is the simplest `function_score`: a single `field_value_factor` that
turns a numeric field directly into a score multiplier. The interesting part
is the `modifier`. A raw `view_count` of 10000 would utterly swamp the text
score, so `log1p` (log of one plus the value) compresses large numbers,
meaning the difference between 100 and 1000 views matters more than the
difference between 9000 and 10000. This reflects how popularity actually
works: the first thousand views tell you a lot, the ten-thousandth tells you
little. The `factor` scales the field before the modifier, and `missing`
supplies a default so documents without the field do not break scoring. With
`boost_mode: multiply`, a relevant-but-unpopular item can still beat a
popular-but-irrelevant one, because both signals contribute.

### Exercise 1.3: Multiple Scoring Functions

See [`03_multi_factor_score.py`](./03_multi_factor_score.py)

**Task:** Add a decay function for products created recently.

Here the single function becomes a `functions` array, which is where
`score_mode` and `boost_mode` finally do different jobs. Each function has its
own `weight` (its relative importance), and `score_mode: sum` adds the
weighted functions together. Note two new tools: a function can carry a
`filter` so it only applies to matching documents (here, a flat `weight: 5`
boost for featured items and `weight: 2` for in-stock items), and `max_boost`
caps the combined function result so no single runaway factor can dominate.
The featured and in-stock filters show a common pattern: use filters for
yes/no business rules and `field_value_factor` for continuous signals.

## Part 2: Decay Functions

Decay functions answer a different question from `field_value_factor`. Instead
of "bigger is better", they express "closer to a target is better". You give
an `origin` (the ideal value), and the score smoothly falls off as a document
moves away from it. They work on dates, numbers, and geographic points alike,
which is why the same shape is reused for recency, distance, and price below.

Every decay function shares three knobs worth understanding:

- `origin`: the point of maximum score (zero distance away).
- `offset`: a grace zone around the origin where there is no decay at all.
- `scale` and `decay`: together they set the falloff rate. The score drops to
  exactly the `decay` value (often `0.5`) once a document is `scale` away from
  the edge of the offset.

The three decay shapes differ in how the curve falls between those points:
`gauss` is bell-shaped and forgiving near the origin then steep, `linear` is
a straight line, and `exp` (exponential) drops fastest right away. Choose the
shape that matches how tolerant your users are of being "a little off".

### Exercise 2.1: Gauss Decay for Recency

See [`04_recency_gauss_decay.py`](./04_recency_gauss_decay.py)

**Task:** Implement linear and exponential decay functions.

This applies `gauss` decay to `created_date` with `origin: now`. The settings
read naturally: `offset: 7d` means anything created in the last week is
treated as equally fresh, and `scale: 30d` with `decay: 0.5` means a product
loses half its freshness boost by roughly a month old. Because the origin is
`now`, the boost is computed at query time and shifts every day, so a product
gradually fades without any reindexing on your part.

### Exercise 2.2: Geographic Distance Decay

See [`05_geo_proximity_decay.py`](./05_geo_proximity_decay.py)

**Task:** Combine distance decay with price range decay.

The same `gauss` function now works on the `geo_point` field, with `scale`
expressed in kilometers. This is why the mapping in Exercise 1.1 declared
`location` as `geo_point`: Elasticsearch computes the real great-circle
distance from the user's `origin` to each product. The `offset: 2km` says
anything within two kilometers is effectively "right here", and the boost
fades over the next ten kilometers. The decay shape does not care whether the
distance is days, dollars, or kilometers; only the units of `scale` change.

### Exercise 2.3: Price Decay for Budget Matching

See [`06_price_preference_decay.py`](./06_price_preference_decay.py)

**Task:** Create a combined decay for both price and rating targets.

Here decay expresses budget matching: the `origin` is the shopper's target
price and `scale` is how flexible they are. This captures a subtle real-world
truth that a simple "cheaper is better" boost would miss, namely that an item
far below budget can look suspiciously cheap and one far above is unaffordable,
so the sweet spot is near the target, not at zero. The same field can be
pulled in two directions by different scoring strategies, which is exactly why
choosing decay over `field_value_factor` is a design decision, not a default.

## Part 3: Script Scoring

When the built-in functions cannot express your logic, `script_score` lets you
write arbitrary scoring code in Painless, Elasticsearch's sandboxed scripting
language. A script runs once per matching document and returns a number that
becomes that document's score contribution. Inside it you read field values
through `doc["field"].value` and combine them with normal math and conditions.
This is the most powerful and the most dangerous tool in the chapter: powerful
because you can compute anything, dangerous because the script executes for
every hit and cannot use the inverted index, so a heavy script slows queries.

### Exercise 3.1: Custom Script Score

See [`07_custom_script_score.py`](./07_custom_script_score.py)

**Task:** Modify the script to include profit margin in scoring.

This script combines several signals that no single built-in function could,
including a computed conversion rate (`sales_count / view_count`) and a
stock penalty. Two details deserve attention. First, it reads `_score`, the
text relevance from the inner query, so it can fold relevance back into the
formula. Second, this query uses `boost_mode: replace`, which throws away the
original query score and uses only the script result. The script keeps things
sensible by multiplying `base_score` back in, but `replace` is a reminder
that `boost_mode` can discard the text relevance entirely if you let it.

### Exercise 3.2: Script with Parameters

See [`08_parameterized_script_score.py`](./08_parameterized_script_score.py)

**Task:** Add category preferences to the scoring parameters.

This version moves the changing values into a `params` block instead of hard
coding them in the script body. This is not just tidiness: Elasticsearch
compiles each distinct script source once and caches the compiled version, so
reusing one parameterized script for every user is far cheaper than sending a
freshly built script string per request. The example feeds in two different
shopper profiles (budget and premium) and the same compiled script produces
personalized rankings purely from the parameters. Reading list parameters
like `params.preferred_brands.contains(...)` shows how rich the inputs can be.

## Part 4: Random Scoring

### Exercise 4.1: Random Score for A/B Testing

See [`09_random_score_ab_test.py`](./09_random_score_ab_test.py)

**Task:** Implement an A/B test with 50/50 split using random scoring.

`random_score` deliberately injects controlled randomness, which sounds odd in
a search engine until you see the use case: showing every user the exact same
ranking starves lower-ranked items of any chance to be seen. The crucial
feature is the `seed`. Using the user's id as the seed makes the randomness
deterministic per user, so the same person sees a stable order across page
reloads while different people see different orders. The example proves this
by running the same user id twice (identical results) and a third user
(different results). Here random scoring is mixed with a rating boost using
`weight` values (0.3 random, 0.7 rating), so results vary without becoming
chaotic, which is the essence of an A/B or exploration test.

## Part 5: Advanced Scoring Strategies

### Exercise 5.1: E-commerce Recommendation Score

See [`10_advanced_ecommerce_score.py`](./10_advanced_ecommerce_score.py)

**Task:** Add seasonal scoring adjustments.

### Exercise 5.2: Click-Through Rate (CTR) Optimization

See [`11_ctr_optimization.py`](./11_ctr_optimization.py)

**Task:** Implement a multi-armed bandit approach for exploration vs
exploitation.

## Part 6: Performance Analysis

### Exercise 6.1: Scoring Performance Comparison

See [`12_scoring_performance_comparison.py`](./12_scoring_performance_comparison.py)

**Task:** Add caching analysis for repeated queries.

## Challenges

### Challenge 1: Personalized Search Engine

Build a personalized search that:

- Tracks user click history
- Learns user preferences over time
- Balances relevance with personalization
- Includes diversity in results

### Challenge 2: Dynamic Pricing Score

Implement scoring that:

- Adjusts based on competitor prices
- Considers demand and supply
- Includes time-based discounting
- Optimizes for profit margin

### Challenge 3: Multi-Objective Optimization

Create a scoring system that balances:

- User satisfaction (ratings, reviews)
- Business metrics (profit, inventory)
- Diversity (categories, brands)
- Freshness (new products)

## Best Practices

```python
best_practices = """
1. **Start Simple**: Begin with basic boosting, add complexity gradually
2. **Test and Measure**: A/B test scoring changes with real users
3. **Cache When Possible**: Function scores can be expensive
4. **Monitor Performance**: Complex scripts can slow down queries
5. **Document Your Logic**: Scoring rules should be well-documented
6. **Use Explain API**: Debug scoring with explain=true
7. **Consider Index-Time Boosting**: Pre-calculate scores when possible
8. **Balance Factors**: Avoid one factor dominating the score
9. **Handle Edge Cases**: Check for missing fields, zero values
10. **Version Your Scoring**: Track scoring algorithm changes
"""
print(best_practices)
```

## Summary Questions

1. When should you use `function_score` vs regular queries?
1. Whats the difference between `boost_mode` and `score_mode`?
1. How do decay functions work and when to use each type?
1. What are the performance implications of script scoring?
1. How can you debug and optimize complex scoring functions?
