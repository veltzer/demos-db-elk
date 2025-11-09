# Custom Scoring Functions with function_score Queries

## Objective
Learn how to implement custom scoring algorithms in Elasticsearch using function_score queries to boost relevance based on business requirements.

## Background
Default Elasticsearch scoring (TF-IDF or BM25) works well for text relevance, but often you need to incorporate business metrics like:
- Popularity, ratings, or views
- Recency or freshness
- Geographic proximity
- User preferences
- Stock levels or availability

## Part 1: Basic Function Score

### Exercise 1.1: Setup Sample E-commerce Data

```python
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import random
import math

es = Elasticsearch(['http://localhost:9200'])

# Delete and create index
if es.indices.exists(index='products'):
    es.indices.delete(index='products')

mapping = {
    'mappings': {
        'properties': {
            'name': {
                'type': 'text',
                'fields': {'keyword': {'type': 'keyword'}}
            },
            'description': {'type': 'text'},
            'category': {'type': 'keyword'},
            'brand': {'type': 'keyword'},
            'price': {'type': 'float'},
            'original_price': {'type': 'float'},
            'rating': {'type': 'float'},
            'review_count': {'type': 'integer'},
            'sales_count': {'type': 'integer'},
            'view_count': {'type': 'integer'},
            'stock_quantity': {'type': 'integer'},
            'is_featured': {'type': 'boolean'},
            'is_on_sale': {'type': 'boolean'},
            'created_date': {'type': 'date'},
            'last_restocked': {'type': 'date'},
            'tags': {'type': 'keyword'},
            'location': {'type': 'geo_point'},
            'profit_margin': {'type': 'float'}
        }
    }
}

es.indices.create(index='products', body=mapping)

# Generate sample products
products = []
categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports']
brands = ['TechPro', 'StyleMax', 'BookWorld', 'HomePlus', 'SportGear']

for i in range(1, 101):
    price = round(random.uniform(10, 500), 2)
    original_price = price * random.uniform(1.0, 1.5)
    created_days_ago = random.randint(1, 365)
    
    product = {
        'name': f'Product {i} - {random.choice(["Premium", "Standard", "Basic", "Pro", "Plus"])}',
        'description': f'High quality product with excellent features and great value. Model {i}',
        'category': random.choice(categories),
        'brand': random.choice(brands),
        'price': price,
        'original_price': round(original_price, 2),
        'rating': round(random.uniform(3.0, 5.0), 1),
        'review_count': random.randint(0, 500),
        'sales_count': random.randint(0, 1000),
        'view_count': random.randint(100, 10000),
        'stock_quantity': random.randint(0, 100),
        'is_featured': random.choice([True, False]),
        'is_on_sale': price < original_price,
        'created_date': (datetime.now() - timedelta(days=created_days_ago)).isoformat(),
        'last_restocked': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
        'tags': random.sample(['bestseller', 'new', 'trending', 'clearance', 'exclusive'], k=random.randint(0, 3)),
        'location': {
            'lat': 40.7128 + random.uniform(-1, 1),
            'lon': -74.0060 + random.uniform(-1, 1)
        },
        'profit_margin': round(random.uniform(0.1, 0.5), 2)
    }
    products.append(product)
    es.index(index='products', id=i, body=product)

es.indices.refresh(index='products')
print(f"Indexed {len(products)} products")
```

**Task:** Create the index and load sample data.

### Exercise 1.2: Simple Field Value Factor

```python
# Boost by popularity (view_count)
def search_with_popularity_boost(query_text):
    query = {
        'query': {
            'function_score': {
                'query': {
                    'match': {
                        'description': query_text
                    }
                },
                'field_value_factor': {
                    'field': 'view_count',
                    'factor': 1.2,
                    'modifier': 'log1p',  # log1p, log, ln, square, sqrt, reciprocal
                    'missing': 1
                },
                'boost_mode': 'multiply'  # multiply, sum, avg, first, max, min
            }
        },
        'size': 5
    }
    
    result = es.search(index='products', body=query)
    
    print(f"\nSearch: '{query_text}' with popularity boost")
    print("-" * 50)
    for hit in result['hits']['hits']:
        product = hit['_source']
        print(f"Score: {hit['_score']:.2f} | Views: {product['view_count']} | {product['name']}")

# Test popularity boosting
search_with_popularity_boost("quality features")
```

**Task:** Modify to boost by rating instead of view_count.

### Exercise 1.3: Multiple Scoring Functions

```python
# Combine multiple scoring factors
def multi_factor_search(query_text):
    query = {
        'query': {
            'function_score': {
                'query': {
                    'match': {
                        'description': query_text
                    }
                },
                'functions': [
                    {
                        'field_value_factor': {
                            'field': 'rating',
                            'factor': 2,
                            'modifier': 'square',
                            'missing': 1
                        },
                        'weight': 3
                    },
                    {
                        'field_value_factor': {
                            'field': 'review_count',
                            'factor': 1.5,
                            'modifier': 'log1p',
                            'missing': 0
                        },
                        'weight': 2
                    },
                    {
                        'filter': {'term': {'is_featured': True}},
                        'weight': 5
                    },
                    {
                        'filter': {'range': {'stock_quantity': {'gt': 0}}},
                        'weight': 2
                    }
                ],
                'score_mode': 'sum',  # sum, avg, first, max, min, multiply
                'boost_mode': 'multiply',
                'max_boost': 10
            }
        },
        'size': 5,
        'explain': False  # Set to True to see scoring details
    }
    
    result = es.search(index='products', body=query)
    
    print(f"\nMulti-factor search: '{query_text}'")
    print("-" * 60)
    print(f"{'Score':<10} {'Rating':<8} {'Reviews':<10} {'Featured':<10} {'Name'}")
    print("-" * 60)
    
    for hit in result['hits']['hits']:
        p = hit['_source']
        featured = 'Yes' if p['is_featured'] else 'No'
        print(f"{hit['_score']:<10.2f} {p['rating']:<8.1f} {p['review_count']:<10} {featured:<10} {p['name'][:30]}")

multi_factor_search("excellent value")
```

**Task:** Add a decay function for products created recently.

## Part 2: Decay Functions

### Exercise 2.1: Gauss Decay for Recency

```python
# Boost recent products using Gaussian decay
def search_with_recency_boost(query_text):
    query = {
        'query': {
            'function_score': {
                'query': {
                    'match': {
                        'description': query_text
                    }
                },
                'functions': [
                    {
                        'gauss': {
                            'created_date': {
                                'origin': 'now',
                                'scale': '30d',  # Half decay at 30 days
                                'offset': '7d',   # No decay for first 7 days
                                'decay': 0.5
                            }
                        },
                        'weight': 2
                    }
                ],
                'boost_mode': 'multiply'
            }
        },
        'size': 5
    }
    
    result = es.search(index='products', body=query)
    
    print(f"\nRecency-boosted search: '{query_text}'")
    print("-" * 50)
    for hit in result['hits']['hits']:
        p = hit['_source']
        days_old = (datetime.now() - datetime.fromisoformat(p['created_date'].replace('Z', '+00:00'))).days
        print(f"Score: {hit['_score']:.2f} | Age: {days_old} days | {p['name']}")

search_with_recency_boost("product features")
```

**Task:** Implement linear and exponential decay functions.

### Exercise 2.2: Geographic Distance Decay

```python
# Boost products based on proximity to user location
def search_by_proximity(query_text, user_location):
    query = {
        'query': {
            'function_score': {
                'query': {
                    'match': {
                        'description': query_text
                    }
                },
                'functions': [
                    {
                        'gauss': {
                            'location': {
                                'origin': user_location,
                                'scale': '10km',
                                'offset': '2km',
                                'decay': 0.5
                            }
                        },
                        'weight': 3
                    }
                ],
                'boost_mode': 'multiply'
            }
        },
        'size': 5
    }
    
    result = es.search(index='products', body=query)
    
    print(f"\nProximity search from {user_location}")
    print("-" * 50)
    for hit in result['hits']['hits']:
        p = hit['_source']
        print(f"Score: {hit['_score']:.2f} | Location: {p['location']} | {p['name'][:40]}")

# Search for products near a specific location
search_by_proximity("quality", {'lat': 40.7, 'lon': -74.0})
```

**Task:** Combine distance decay with price range decay.

### Exercise 2.3: Price Decay for Budget Matching

```python
# Boost products near a target price point
def search_with_price_preference(query_text, target_price, price_flexibility):
    query = {
        'query': {
            'function_score': {
                'query': {
                    'match': {
                        'description': query_text
                    }
                },
                'functions': [
                    {
                        'gauss': {
                            'price': {
                                'origin': target_price,
                                'scale': price_flexibility,  # e.g., "50" for ±$50
                                'decay': 0.5
                            }
                        },
                        'weight': 2
                    }
                ],
                'boost_mode': 'multiply'
            }
        },
        'size': 10
    }
    
    result = es.search(index='products', body=query)
    
    print(f"\nPrice-optimized search (target: ${target_price} ± ${price_flexibility})")
    print("-" * 60)
    for hit in result['hits']['hits']:
        p = hit['_source']
        price_diff = abs(p['price'] - target_price)
        print(f"Score: {hit['_score']:.2f} | Price: ${p['price']} (Δ${price_diff:.2f}) | {p['name'][:30]}")

search_with_price_preference("product", target_price=100, price_flexibility=30)
```

**Task:** Create a combined decay for both price and rating targets.

## Part 3: Script Scoring

### Exercise 3.1: Custom Script Score

```python
# Use Painless script for complex scoring logic
def search_with_script_score(query_text):
    query = {
        'query': {
            'function_score': {
                'query': {
                    'match': {
                        'description': query_text
                    }
                },
                'functions': [
                    {
                        'script_score': {
                            'script': {
                                'source': """
                                    // Custom scoring algorithm
                                    double base_score = _score;
                                    double rating_boost = doc['rating'].value * 2;
                                    double review_boost = Math.log(1 + doc['review_count'].value);
                                    double sales_boost = Math.log(1 + doc['sales_count'].value);
                                    double stock_penalty = doc['stock_quantity'].value > 0 ? 1.0 : 0.5;
                                    double sale_boost = doc['is_on_sale'].value ? 1.5 : 1.0;
                                    
                                    // Calculate conversion rate
                                    double views = doc['view_count'].value;
                                    double sales = doc['sales_count'].value;
                                    double conversion_rate = views > 0 ? sales / views : 0;
                                    double conversion_boost = 1 + (conversion_rate * 10);
                                    
                                    return base_score * rating_boost * review_boost * 
                                           sales_boost * stock_penalty * sale_boost * conversion_boost;
                                """
                            }
                        }
                    }
                ],
                'boost_mode': 'replace'  # Replace original score with script score
            }
        },
        'size': 5,
        'explain': False
    }
    
    result = es.search(index='products', body=query)
    
    print(f"\nScript-scored search: '{query_text}'")
    print("-" * 80)
    print(f"{'Score':<12} {'Rating':<8} {'Reviews':<10} {'Sales':<10} {'Conv Rate':<12} {'Name'}")
    print("-" * 80)
    
    for hit in result['hits']['hits']:
        p = hit['_source']
        conv_rate = p['sales_count'] / p['view_count'] if p['view_count'] > 0 else 0
        print(f"{hit['_score']:<12.2f} {p['rating']:<8.1f} {p['review_count']:<10} "
              f"{p['sales_count']:<10} {conv_rate:<12.4f} {p['name'][:25]}")

search_with_script_score("excellent features")
```

**Task:** Modify the script to include profit margin in scoring.

### Exercise 3.2: Script with Parameters

```python
# Parameterized script for flexible scoring
def search_with_params(query_text, user_preferences):
    query = {
        'query': {
            'function_score': {
                'query': {
                    'match': {
                        'description': query_text
                    }
                },
                'functions': [
                    {
                        'script_score': {
                            'script': {
                                'source': """
                                    double score = _score;
                                    
                                    // Apply user preference weights
                                    score *= Math.pow(doc['rating'].value / 5.0, params.rating_weight);
                                    score *= Math.pow(Math.log(2 + doc['review_count'].value) / 10, params.popularity_weight);
                                    
                                    // Price sensitivity
                                    if (params.max_price > 0 && doc['price'].value > params.max_price) {
                                        score *= 0.5;  // Penalize over-budget items
                                    }
                                    
                                    // Brand preference
                                    if (params.preferred_brands.contains(doc['brand'].value)) {
                                        score *= params.brand_boost;
                                    }
                                    
                                    return score;
                                """,
                                'params': user_preferences
                            }
                        }
                    }
                ],
                'boost_mode': 'replace'
            }
        },
        'size': 5
    }
    
    result = es.search(index='products', body=query)
    
    print(f"\nPersonalized search with user preferences")
    print(f"Preferences: {user_preferences}")
    print("-" * 60)
    for hit in result['hits']['hits']:
        p = hit['_source']
        print(f"Score: {hit['_score']:.2f} | ${p['price']} | {p['brand']} | {p['name'][:30]}")

# Different user profiles
budget_shopper = {
    'rating_weight': 1,
    'popularity_weight': 2,
    'max_price': 100,
    'preferred_brands': ['BookWorld', 'HomePlus'],
    'brand_boost': 1.5
}

premium_shopper = {
    'rating_weight': 3,
    'popularity_weight': 1,
    'max_price': 0,  # No budget limit
    'preferred_brands': ['TechPro', 'StyleMax'],
    'brand_boost': 2.0
}

search_with_params("quality product", budget_shopper)
search_with_params("quality product", premium_shopper)
```

**Task:** Add category preferences to the scoring parameters.

## Part 4: Random Scoring

### Exercise 4.1: Random Score for A/B Testing

```python
# Random scoring for result variation
def search_with_randomization(query_text, user_id):
    query = {
        'query': {
            'function_score': {
                'query': {
                    'match': {
                        'description': query_text
                    }
                },
                'functions': [
                    {
                        'random_score': {
                            'seed': user_id,  # Same seed = same random order for user
                            'field': '_seq_no'
                        },
                        'weight': 0.3  # Control randomness strength
                    },
                    {
                        'field_value_factor': {
                            'field': 'rating',
                            'factor': 2
                        },
                        'weight': 0.7
                    }
                ],
                'score_mode': 'sum',
                'boost_mode': 'multiply'
            }
        },
        'size': 5
    }
    
    print(f"\nRandomized search for user {user_id}")
    print("-" * 50)
    
    result = es.search(index='products', body=query)
    for hit in result['hits']['hits']:
        p = hit['_source']
        print(f"Score: {hit['_score']:.2f} | Rating: {p['rating']} | {p['name'][:40]}")

# Same user gets consistent results
search_with_randomization("product", user_id=12345)
search_with_randomization("product", user_id=12345)  # Same results

# Different user gets different results
search_with_randomization("product", user_id=67890)
```

**Task:** Implement an A/B test with 50/50 split using random scoring.

## Part 5: Advanced Scoring Strategies

### Exercise 5.1: E-commerce Recommendation Score

```python
def advanced_ecommerce_scoring(query_text, user_context):
    """
    Complex scoring for e-commerce with:
    - Business goals (profit, inventory)
    - User context (history, preferences)
    - Item quality (ratings, returns)
    - Temporal factors (trends, seasons)
    """
    
    query = {
        'query': {
            'function_score': {
                'query': {
                    'bool': {
                        'should': [
                            {'match': {'name': {'query': query_text, 'boost': 2}}},
                            {'match': {'description': query_text}},
                            {'match': {'tags': {'query': query_text, 'boost': 1.5}}}
                        ],
                        'minimum_should_match': 1
                    }
                },
                'functions': [
                    # Business metrics
                    {
                        'field_value_factor': {
                            'field': 'profit_margin',
                            'factor': 3,
                            'modifier': 'square'
                        },
                        'weight': user_context.get('business_weight', 1)
                    },
                    # Inventory management - boost high stock items
                    {
                        'filter': {'range': {'stock_quantity': {'gt': 50}}},
                        'weight': 2
                    },
                    # Clear low stock items
                    {
                        'filter': {
                            'bool': {
                                'must': [
                                    {'range': {'stock_quantity': {'gt': 0, 'lte': 10}}},
                                    {'term': {'is_on_sale': True}}
                                ]
                            }
                        },
                        'weight': 3
                    },
                    # Quality signals
                    {
                        'script_score': {
                            'script': {
                                'source': """
                                    // Bayesian average for ratings
                                    double C = 10;  // Minimum reviews for credibility
                                    double m = 4.0; // Prior mean rating
                                    double reviews = doc['review_count'].value;
                                    double rating = doc['rating'].value;
                                    
                                    double bayesian_rating = (C * m + reviews * rating) / (C + reviews);
                                    return Math.pow(bayesian_rating / 5.0, 2);
                                """
                            }
                        },
                        'weight': 4
                    },
                    # Trending items (high recent sales)
                    {
                        'gauss': {
                            'last_restocked': {
                                'origin': 'now',
                                'scale': '7d',
                                'decay': 0.5
                            }
                        },
                        'weight': 2
                    },
                    # Personalization based on category preference
                    {
                        'filter': {'terms': {'category': user_context.get('preferred_categories', [])}},
                        'weight': 3
                    }
                ],
                'score_mode': 'sum',
                'boost_mode': 'multiply',
                'max_boost': 20
            }
        },
        'size': 10,
        '_source': ['name', 'price', 'rating', 'review_count', 'profit_margin', 'stock_quantity'],
        'explain': False
    }
    
    result = es.search(index='products', body=query)
    
    print(f"\nAdvanced E-commerce Scoring")
    print(f"Query: '{query_text}'")
    print(f"User Context: {user_context}")
    print("-" * 80)
    print(f"{'Score':<10} {'Price':<10} {'Rating':<10} {'Reviews':<10} {'Margin':<10} {'Stock':<10} {'Name'}")
    print("-" * 80)
    
    for hit in result['hits']['hits']:
        p = hit['_source']
        print(f"{hit['_score']:<10.2f} ${p['price']:<9.2f} {p['rating']:<10.1f} "
              f"{p['review_count']:<10} {p['profit_margin']:<10.2f} {p['stock_quantity']:<10} "
              f"{p['name'][:20]}")

# Different user contexts
regular_user = {
    'business_weight': 1,
    'preferred_categories': ['Electronics', 'Books']
}

vip_user = {
    'business_weight': 0.5,  # Less focus on profit for VIP
    'preferred_categories': ['Electronics', 'Sports']
}

advanced_ecommerce_scoring("premium", regular_user)
advanced_ecommerce_scoring("premium", vip_user)
```

**Task:** Add seasonal scoring adjustments.

### Exercise 5.2: Click-Through Rate (CTR) Optimization

```python
# Scoring based on historical click-through rates
def ctr_optimized_search(query_text):
    # First, update some products with CTR data
    ctr_updates = [
        {'id': 1, 'clicks': 150, 'impressions': 1000},
        {'id': 2, 'clicks': 300, 'impressions': 2000},
        {'id': 3, 'clicks': 50, 'impressions': 1500},
        {'id': 4, 'clicks': 500, 'impressions': 3000},
        {'id': 5, 'clicks': 75, 'impressions': 500}
    ]
    
    for update in ctr_updates:
        es.update(
            index='products',
            id=update['id'],
            body={
                'doc': {
                    'clicks': update['clicks'],
                    'impressions': update['impressions']
                }
            }
        )
    
    es.indices.refresh(index='products')
    
    # Search with CTR optimization
    query = {
        'query': {
            'function_score': {
                'query': {
                    'match': {
                        'description': query_text
                    }
                },
                'functions': [
                    {
                        'script_score': {
                            'script': {
                                'source': """
                                    if (!doc.containsKey('clicks') || !doc.containsKey('impressions')) {
                                        return 1.0;
                                    }
                                    
                                    double clicks = doc['clicks'].value;
                                    double impressions = doc['impressions'].value;
                                    
                                    if (impressions == 0) return 1.0;
                                    
                                    // Wilson score interval for CTR
                                    double ctr = clicks / impressions;
                                    double z = 1.96; // 95% confidence
                                    double n = impressions;
                                    
                                    double center = ctr + z*z/(2*n);
                                    double spread = z * Math.sqrt(ctr*(1-ctr)/n + z*z/(4*n*n));
                                    double denominator = 1 + z*z/n;
                                    
                                    double lower_bound = (center - spread) / denominator;
                                    
                                    return 1 + (lower_bound * 10); // Scale the CTR boost
                                """
                            }
                        }
                    }
                ],
                'boost_mode': 'multiply'
            }
        },
        'size': 5
    }
    
    result = es.search(index='products', body=query)
    
    print(f"\nCTR-Optimized Search: '{query_text}'")
    print("-" * 60)
    for hit in result['hits']['hits']:
        p = hit['_source']
        ctr = 0
        if 'clicks' in p and 'impressions' in p and p['impressions'] > 0:
            ctr = p['clicks'] / p['impressions']
        print(f"Score: {hit['_score']:.2f} | CTR: {ctr:.3f} | {p['name'][:40]}")

ctr_optimized_search("quality product")
```

**Task:** Implement a multi-armed bandit approach for exploration vs exploitation.

## Part 6: Performance Analysis

### Exercise 6.1: Scoring Performance Comparison

```python
import time

def compare_scoring_performance():
    """Compare performance of different scoring strategies"""
    
    queries = [
        {
            'name': 'Basic match',
            'body': {
                'query': {'match': {'description': 'product'}}
            }
        },
        {
            'name': 'Simple function_score',
            'body': {
                'query': {
                    'function_score': {
                        'query': {'match': {'description': 'product'}},
                        'field_value_factor': {'field': 'rating'}
                    }
                }
            }
        },
        {
            'name': 'Multiple functions',
            'body': {
                'query': {
                    'function_score': {
                        'query': {'match': {'description': 'product'}},
                        'functions': [
                            {'field_value_factor': {'field': 'rating'}},
                            {'field_value_factor': {'field': 'review_count'}},
                            {'filter': {'term': {'is_featured': True}}, 'weight': 2}
                        ]
                    }
                }
            }
        },
        {
            'name': 'Script scoring',
            'body': {
                'query': {
                    'function_score': {
                        'query': {'match': {'description': 'product'}},
                        'script_score': {
                            'script': {
                                'source': 'Math.log(2 + doc["rating"].value) * _score'
                            }
                        }
                    }
                }
            }
        }
    ]
    
    print("\nScoring Performance Comparison")
    print("-" * 60)
    print(f"{'Query Type':<25} {'Avg Time (ms)':<15} {'Results':<10}")
    print("-" * 60)
    
    for query_config in queries:
        times = []
        for _ in range(10):
            start = time.perf_counter()
            result = es.search(index='products', body=query_config['body'], size=10)
            times.append((time.perf_counter() - start) * 1000)
        
        avg_time = sum(times) / len(times)
        hit_count = result['hits']['total']['value']
        
        print(f"{query_config['name']:<25} {avg_time:<15.2f} {hit_count:<10}")

compare_scoring_performance()
```

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

1. When should you use function_score vs regular queries?
2. What's the difference between boost_mode and score_mode?
3. How do decay functions work and when to use each type?
4. What are the performance implications of script scoring?
5. How can you debug and optimize complex scoring functions?
