# Exercise 7: Parent-Child Relationship Model for Hierarchical Data

## Objective
Learn how to model hierarchical relationships in Elasticsearch using parent-child joins, understand their use cases, performance implications, and query patterns.

## Background
Parent-child relationships allow you to model hierarchical data where documents have relationships with other documents. Common use cases include:
- Blog posts and comments
- Products and reviews
- Companies and employees
- Questions and answers

## Part 1: Setting Up Parent-Child Mapping

### Exercise 1.1: Create Index with Join Field

```python
from elasticsearch import Elasticsearch
from datetime import datetime
import json

es = Elasticsearch(['http://localhost:9200'])

# Delete index if exists
if es.indices.exists(index='blog_system'):
    es.indices.delete(index='blog_system')

# Create index with parent-child relationship
mapping = {
    'mappings': {
        'properties': {
            'join_field': {
                'type': 'join',
                'relations': {
                    'blog_post': ['comment', 'author_note'],  # blog_post can have comments and author_notes
                    'comment': 'reply'  # comments can have replies
                }
            },
            'title': {'type': 'text'},
            'content': {'type': 'text'},
            'author': {'type': 'keyword'},
            'created_at': {'type': 'date'},
            'tags': {'type': 'keyword'},
            'views': {'type': 'integer'},
            'likes': {'type': 'integer'},
            'status': {'type': 'keyword'}
        }
    }
}

es.indices.create(index='blog_system', body=mapping)
print("Index created with parent-child relationship")
```

**Task:** Create the index and understand the join field structure.

### Exercise 1.2: Index Parent Documents (Blog Posts)

```python
# Index blog posts (parent documents)
blog_posts = [
    {
        'title': 'Getting Started with Elasticsearch',
        'content': 'Elasticsearch is a powerful search engine that provides full-text search capabilities...',
        'author': 'alice_tech',
        'created_at': '2024-01-15T10:00:00',
        'tags': ['elasticsearch', 'search', 'tutorial'],
        'views': 1500,
        'likes': 45,
        'status': 'published',
        'join_field': 'blog_post'  # Marking as parent type
    },
    {
        'title': 'Advanced Query DSL Techniques',
        'content': 'In this post, we will explore advanced Query DSL features including bool queries...',
        'author': 'bob_dev',
        'created_at': '2024-01-20T14:30:00',
        'tags': ['elasticsearch', 'query-dsl', 'advanced'],
        'views': 2300,
        'likes': 78,
        'status': 'published',
        'join_field': 'blog_post'
    },
    {
        'title': 'Scaling Elasticsearch Clusters',
        'content': 'Learn how to properly scale your Elasticsearch cluster for production workloads...',
        'author': 'charlie_ops',
        'created_at': '2024-02-01T09:15:00',
        'tags': ['elasticsearch', 'scaling', 'production'],
        'views': 3200,
        'likes': 92,
        'status': 'published',
        'join_field': 'blog_post'
    }
]

# Index parent documents
for i, post in enumerate(blog_posts, 1):
    es.index(index='blog_system', id=f'post_{i}', body=post)
    print(f"Indexed blog post: {post['title']}")

# Refresh to make documents searchable
es.indices.refresh(index='blog_system')
```

**Task:** Index the parent documents and note how the join_field is set.

### Exercise 1.3: Index Child Documents (Comments)

```python
# Index comments (child documents)
comments = [
    {
        'content': 'Great tutorial! This helped me understand the basics.',
        'author': 'user_john',
        'created_at': '2024-01-15T12:30:00',
        'likes': 5,
        'join_field': {
            'name': 'comment',
            'parent': 'post_1'  # Reference to parent document ID
        }
    },
    {
        'content': 'Could you add more examples about aggregations?',
        'author': 'user_jane',
        'created_at': '2024-01-15T15:45:00',
        'likes': 3,
        'join_field': {
            'name': 'comment',
            'parent': 'post_1'
        }
    },
    {
        'content': 'The bool query section is excellent!',
        'author': 'user_mike',
        'created_at': '2024-01-21T10:00:00',
        'likes': 8,
        'join_field': {
            'name': 'comment',
            'parent': 'post_2'
        }
    },
    {
        'content': 'How does this compare to using nested queries?',
        'author': 'user_sarah',
        'created_at': '2024-01-21T11:30:00',
        'likes': 6,
        'join_field': {
            'name': 'comment',
            'parent': 'post_2'
        }
    }
]

# Index child documents with routing
for i, comment in enumerate(comments, 1):
    parent_id = comment['join_field']['parent']
    es.index(
        index='blog_system',
        id=f'comment_{i}',
        body=comment,
        routing=parent_id  # IMPORTANT: routing required for child documents
    )
    print(f"Indexed comment for {parent_id}")

es.indices.refresh(index='blog_system')
```

**Task:** Index child documents and understand why routing is required.

### Exercise 1.4: Index Grandchild Documents (Replies to Comments)

```python
# Index replies to comments (grandchild documents)
replies = [
    {
        'content': 'I agree! The examples are very clear.',
        'author': 'user_alice',
        'created_at': '2024-01-15T13:00:00',
        'likes': 2,
        'join_field': {
            'name': 'reply',
            'parent': 'comment_1'  # Reply to comment_1
        }
    },
    {
        'content': 'Check out the official documentation for more aggregation examples.',
        'author': 'alice_tech',  # Author replying
        'created_at': '2024-01-15T16:00:00',
        'likes': 4,
        'join_field': {
            'name': 'reply',
            'parent': 'comment_2'
        }
    }
]

# Index replies with proper routing (must route to the root parent)
for i, reply in enumerate(replies, 1):
    # For replies, we need to route to the blog post (root parent)
    # In this case, comment_1 and comment_2 both belong to post_1
    es.index(
        index='blog_system',
        id=f'reply_{i}',
        body=reply,
        routing='post_1'  # Route to root parent (blog post)
    )
    print(f"Indexed reply to {reply['join_field']['parent']}")

es.indices.refresh(index='blog_system')
```

**Task:** Understand the routing requirements for multi-level hierarchies.

## Part 2: Querying Parent-Child Relationships

### Exercise 2.1: Has Child Query

```python
# Find blog posts that have comments from a specific user
has_child_query = {
    'query': {
        'has_child': {
            'type': 'comment',
            'query': {
                'term': {
                    'author': 'user_jane'
                }
            }
        }
    }
}

result = es.search(index='blog_system', body=has_child_query)
print("Blog posts with comments from user_jane:")
for hit in result['hits']['hits']:
    print(f"- {hit['_source']['title']}")
```

**Task:** Find all blog posts that have at least one comment.

### Exercise 2.2: Has Parent Query

```python
# Find comments for blog posts with specific tags
has_parent_query = {
    'query': {
        'has_parent': {
            'parent_type': 'blog_post',
            'query': {
                'term': {
                    'tags': 'tutorial'
                }
            }
        }
    }
}

result = es.search(index='blog_system', body=has_parent_query)
print("Comments on tutorial posts:")
for hit in result['hits']['hits']:
    print(f"- {hit['_source']['content'][:50]}... by {hit['_source']['author']}")
```

**Task:** Find all comments on posts authored by a specific user.

### Exercise 2.3: Parent ID Query

```python
# Get all children of a specific parent
parent_id_query = {
    'query': {
        'parent_id': {
            'type': 'comment',
            'id': 'post_1'
        }
    }
}

result = es.search(index='blog_system', body=parent_id_query)
print(f"Comments on post_1: {result['hits']['total']['value']}")
for hit in result['hits']['hits']:
    print(f"- {hit['_source']['author']}: {hit['_source']['content'][:50]}...")
```

**Task:** Retrieve all comments for a specific blog post.

### Exercise 2.4: Children Aggregation

```python
# Get blog posts with comment count
children_agg_query = {
    'query': {
        'term': {'join_field': 'blog_post'}
    },
    'aggs': {
        'comment_count': {
            'children': {
                'type': 'comment'
            },
            'aggs': {
                'top_commenters': {
                    'terms': {
                        'field': 'author',
                        'size': 5
                    }
                }
            }
        }
    }
}

result = es.search(index='blog_system', body=children_agg_query)
print("Top commenters across all blog posts:")
if 'comment_count' in result['aggregations']:
    for bucket in result['aggregations']['comment_count']['top_commenters']['buckets']:
        print(f"- {bucket['key']}: {bucket['doc_count']} comments")
```

**Task:** Calculate the average number of likes on comments per blog post.

## Part 3: Advanced Parent-Child Patterns

### Exercise 3.1: Inner Hits - Getting Related Documents

```python
# Get blog posts with their comments included
inner_hits_query = {
    'query': {
        'has_child': {
            'type': 'comment',
            'query': {'match_all': {}},
            'inner_hits': {
                'size': 3,
                'sort': [{'likes': {'order': 'desc'}}]
            }
        }
    }
}

result = es.search(index='blog_system', body=inner_hits_query)
print("Blog posts with their top comments:")
for hit in result['hits']['hits']:
    print(f"\nPost: {hit['_source']['title']}")
    if 'inner_hits' in hit:
        print("  Top comments:")
        for comment in hit['inner_hits']['comment']['hits']['hits']:
            print(f"    - {comment['_source']['author']}: {comment['_source']['content'][:40]}...")
```

**Task:** Retrieve blog posts with their most recent 5 comments.

### Exercise 3.2: Scoring with Child Documents

```python
# Score blog posts based on comment activity
scoring_query = {
    'query': {
        'has_child': {
            'type': 'comment',
            'score_mode': 'sum',  # sum, avg, min, max, none
            'query': {
                'function_score': {
                    'query': {'match_all': {}},
                    'field_value_factor': {
                        'field': 'likes',
                        'factor': 1.5,
                        'modifier': 'log1p'
                    }
                }
            }
        }
    }
}

result = es.search(index='blog_system', body=scoring_query)
print("Blog posts scored by comment engagement:")
for hit in result['hits']['hits']:
    print(f"- {hit['_source']['title']} (score: {hit['_score']:.2f})")
```

**Task:** Score blog posts based on the number of comments they have.

### Exercise 3.3: Complex Multi-Level Queries

```python
# Find blog posts that have comments with replies
multi_level_query = {
    'query': {
        'has_child': {
            'type': 'comment',
            'query': {
                'has_child': {
                    'type': 'reply',
                    'query': {'match_all': {}}
                }
            }
        }
    }
}

result = es.search(index='blog_system', body=multi_level_query)
print("Blog posts with comments that have replies:")
for hit in result['hits']['hits']:
    print(f"- {hit['_source']['title']}")
```

**Task:** Find comments that have replies from the original post author.

## Part 4: Performance Considerations

### Exercise 4.1: Compare Parent-Child vs Nested Performance

```python
import time

def measure_parent_child_performance():
    """Measure query performance for parent-child relationships"""
    
    # Warm up
    es.search(index='blog_system', body={'query': {'match_all': {}}})
    
    queries = [
        {
            'name': 'Simple parent query',
            'body': {'query': {'term': {'join_field': 'blog_post'}}}
        },
        {
            'name': 'Has child query',
            'body': {'query': {'has_child': {'type': 'comment', 'query': {'match_all': {}}}}}
        },
        {
            'name': 'Has parent query',
            'body': {'query': {'has_parent': {'parent_type': 'blog_post', 'query': {'match_all': {}}}}}
        },
        {
            'name': 'Parent-child with aggregation',
            'body': {
                'query': {'term': {'join_field': 'blog_post'}},
                'aggs': {'comments': {'children': {'type': 'comment'}}}
            }
        }
    ]
    
    print("\nParent-Child Query Performance:")
    print("-" * 50)
    
    for query in queries:
        times = []
        for _ in range(10):
            start = time.perf_counter()
            es.search(index='blog_system', body=query['body'])
            times.append((time.perf_counter() - start) * 1000)
        
        avg_time = sum(times) / len(times)
        print(f"{query['name']}: {avg_time:.2f}ms")

measure_parent_child_performance()
```

**Task:** Compare the performance of different parent-child query types.

### Exercise 4.2: Create Alternative Denormalized Structure

```python
# Alternative: Denormalized structure for comparison
if es.indices.exists(index='blog_denormalized'):
    es.indices.delete(index='blog_denormalized')

denormalized_mapping = {
    'mappings': {
        'properties': {
            'title': {'type': 'text'},
            'content': {'type': 'text'},
            'author': {'type': 'keyword'},
            'comments': {
                'type': 'nested',
                'properties': {
                    'content': {'type': 'text'},
                    'author': {'type': 'keyword'},
                    'created_at': {'type': 'date'},
                    'likes': {'type': 'integer'}
                }
            }
        }
    }
}

es.indices.create(index='blog_denormalized', body=denormalized_mapping)

# Index denormalized document
denormalized_doc = {
    'title': 'Getting Started with Elasticsearch',
    'content': 'Elasticsearch is a powerful search engine...',
    'author': 'alice_tech',
    'comments': [
        {
            'content': 'Great tutorial! This helped me understand the basics.',
            'author': 'user_john',
            'created_at': '2024-01-15T12:30:00',
            'likes': 5
        },
        {
            'content': 'Could you add more examples about aggregations?',
            'author': 'user_jane',
            'created_at': '2024-01-15T15:45:00',
            'likes': 3
        }
    ]
}

es.index(index='blog_denormalized', id='post_1', body=denormalized_doc)
print("\nCreated denormalized structure for comparison")
```

**Task:** Compare query complexity between parent-child and nested approaches.

## Part 5: Real-World Scenarios

### Exercise 5.1: E-commerce Product Reviews

```python
# Create an e-commerce scenario with products and reviews
if es.indices.exists(index='ecommerce'):
    es.indices.delete(index='ecommerce')

ecommerce_mapping = {
    'mappings': {
        'properties': {
            'join_field': {
                'type': 'join',
                'relations': {
                    'product': 'review'
                }
            },
            'name': {'type': 'text'},
            'description': {'type': 'text'},
            'category': {'type': 'keyword'},
            'price': {'type': 'float'},
            'rating': {'type': 'float'},
            'review_text': {'type': 'text'},
            'reviewer': {'type': 'keyword'},
            'verified_purchase': {'type': 'boolean'},
            'helpful_votes': {'type': 'integer'},
            'created_at': {'type': 'date'}
        }
    }
}

es.indices.create(index='ecommerce', body=ecommerce_mapping)

# Index products
products = [
    {
        'name': 'Wireless Headphones Pro',
        'description': 'Premium noise-cancelling wireless headphones',
        'category': 'Electronics',
        'price': 299.99,
        'join_field': 'product'
    },
    {
        'name': 'Smart Watch Ultra',
        'description': 'Advanced fitness and health tracking smartwatch',
        'category': 'Electronics',
        'price': 399.99,
        'join_field': 'product'
    }
]

for i, product in enumerate(products, 1):
    es.index(index='ecommerce', id=f'product_{i}', body=product)

# Index reviews
reviews = [
    {
        'rating': 5,
        'review_text': 'Amazing sound quality and comfort!',
        'reviewer': 'john_doe',
        'verified_purchase': True,
        'helpful_votes': 45,
        'created_at': '2024-01-10',
        'join_field': {'name': 'review', 'parent': 'product_1'}
    },
    {
        'rating': 4,
        'review_text': 'Good but battery could be better',
        'reviewer': 'jane_smith',
        'verified_purchase': True,
        'helpful_votes': 23,
        'created_at': '2024-01-15',
        'join_field': {'name': 'review', 'parent': 'product_1'}
    }
]

for i, review in enumerate(reviews, 1):
    parent_id = review['join_field']['parent']
    es.index(index='ecommerce', id=f'review_{i}', body=review, routing=parent_id)

es.indices.refresh(index='ecommerce')

# Query: Find products with average rating above 4
avg_rating_query = {
    'query': {
        'has_child': {
            'type': 'review',
            'query': {'match_all': {}},
            'inner_hits': {
                'size': 0,
                '_source': False
            }
        }
    },
    'aggs': {
        'products': {
            'terms': {
                'field': 'name.keyword',
                'size': 10
            },
            'aggs': {
                'avg_rating': {
                    'children': {
                        'type': 'review'
                    },
                    'aggs': {
                        'rating': {
                            'avg': {
                                'field': 'rating'
                            }
                        }
                    }
                }
            }
        }
    }
}

# Note: This is a simplified example. In practice, you'd need more complex aggregations
print("Products with reviews (example query created)")
```

**Task:** Create queries to find:
1. Products with more than 10 reviews
2. Products where all reviews are verified purchases
3. The top-rated products in each category

### Exercise 5.2: Company Organization Structure

```python
# Model a company organization structure
org_mapping = {
    'mappings': {
        'properties': {
            'join_field': {
                'type': 'join',
                'relations': {
                    'company': 'department',
                    'department': 'employee'
                }
            },
            'name': {'type': 'text'},
            'type': {'type': 'keyword'},
            'budget': {'type': 'float'},
            'employee_count': {'type': 'integer'},
            'position': {'type': 'keyword'},
            'salary': {'type': 'float'},
            'hire_date': {'type': 'date'}
        }
    }
}

# Task: Create the index and model a company hierarchy
print("Organization structure mapping created (implement indexing)")
```

**Task:** Implement a complete company hierarchy with:
1. Company -> Departments -> Employees
2. Queries to find departments over budget
3. Aggregations for salary statistics by department

## Best Practices and Considerations

### When to Use Parent-Child:
1. **One-to-many relationships** where children are frequently updated independently
2. **Large child sets** that would make nested documents too large
3. **Need to query children independently** from parents
4. **Different update frequencies** between parent and child

### When NOT to Use Parent-Child:
1. **Small datasets** - Overhead not worth it
2. **Rarely queried relationships** - Denormalization might be better
3. **Need high query performance** - Parent-child queries are slower
4. **Simple aggregations** - Nested might be sufficient

### Performance Tips:
```python
performance_tips = """
1. Always use routing for child documents
2. Keep parent-child hierarchies shallow (max 2-3 levels)
3. Use eager_global_ordinals for frequently queried join fields
4. Consider denormalization for read-heavy workloads
5. Monitor memory usage - join fields use global ordinals
6. Use has_child/has_parent queries sparingly
7. Prefer parent_id queries when possible
"""
print(performance_tips)
```

## Challenges

### Challenge 1: Multi-tenant Blog System
Design and implement a multi-tenant blog system where:
- Each tenant has multiple blogs
- Each blog has multiple posts
- Each post has comments and ratings
- Comments can have nested replies

### Challenge 2: Product Catalog with Variants
Create a product catalog where:
- Products have multiple variants (size, color)
- Each variant has its own inventory
- Products have reviews
- Calculate aggregate ratings considering all reviews

### Challenge 3: Migration Strategy
Write a script to migrate from a parent-child structure to a denormalized structure and compare:
- Index size
- Query performance
- Update performance
- Memory usage

## Summary Questions

1. When should you use parent-child vs nested documents?
2. Why is routing required for child documents?
3. What are the performance implications of parent-child relationships?
4. How do inner_hits work and when should you use them?
5. What are the limitations of parent-child relationships in Elasticsearch?