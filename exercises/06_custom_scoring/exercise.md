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

## Part 1: Basic Function Score

### Exercise 1.1: Setup Sample E-commerce Data

See [`01_setup_sample_products.py`](./01_setup_sample_products.py)

**Task:** Create the index and load sample data.

### Exercise 1.2: Simple Field Value Factor

See [`02_popularity_boost.py`](./02_popularity_boost.py)

**Task:** Modify to boost by rating instead of view_count.

### Exercise 1.3: Multiple Scoring Functions

See [`03_multi_factor_score.py`](./03_multi_factor_score.py)

**Task:** Add a decay function for products created recently.

## Part 2: Decay Functions

### Exercise 2.1: Gauss Decay for Recency

See [`04_recency_gauss_decay.py`](./04_recency_gauss_decay.py)

**Task:** Implement linear and exponential decay functions.

### Exercise 2.2: Geographic Distance Decay

See [`05_geo_proximity_decay.py`](./05_geo_proximity_decay.py)

**Task:** Combine distance decay with price range decay.

### Exercise 2.3: Price Decay for Budget Matching

See [`06_price_preference_decay.py`](./06_price_preference_decay.py)

**Task:** Create a combined decay for both price and rating targets.

## Part 3: Script Scoring

### Exercise 3.1: Custom Script Score

See [`07_custom_script_score.py`](./07_custom_script_score.py)

**Task:** Modify the script to include profit margin in scoring.

### Exercise 3.2: Script with Parameters

See [`08_parameterized_script_score.py`](./08_parameterized_script_score.py)

**Task:** Add category preferences to the scoring parameters.

## Part 4: Random Scoring

### Exercise 4.1: Random Score for A/B Testing

See [`09_random_score_ab_test.py`](./09_random_score_ab_test.py)

**Task:** Implement an A/B test with 50/50 split using random scoring.

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
