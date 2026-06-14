# Parent-Child Relationship Model for Hierarchical Data

## Objective

Learn how to model hierarchical relationships in Elasticsearch using
parent-child joins, understand their use cases, performance implications, and
query patterns.

## Background

Parent-child relationships allow you to model hierarchical data where documents
have relationships with other documents. Common use cases include:

- Blog posts and comments
- Products and reviews
- Companies and employees
- Questions and answers

## Part 1: Setting Up Parent-Child Mapping

### Exercise 1.1: Create Index with Join Field

See [`01_create_join_index.py`](./01_create_join_index.py)

**Task:** Create the index and understand the join field structure.

### Exercise 1.2: Index Parent Documents (Blog Posts)

See [`02_index_parent_blog_posts.py`](./02_index_parent_blog_posts.py)

**Task:** Index the parent documents and note how the `join_field` is set.

### Exercise 1.3: Index Child Documents (Comments)

See [`03_index_child_comments.py`](./03_index_child_comments.py)

**Task:** Index child documents and understand why routing is required.

### Exercise 1.4: Index Grandchild Documents (Replies to Comments)

See [`04_index_grandchild_replies.py`](./04_index_grandchild_replies.py)

**Task:** Understand the routing requirements for multi-level hierarchies.

## Part 2: Querying Parent-Child Relationships

### Exercise 2.1: Has Child Query

See [`05_has_child_query.py`](./05_has_child_query.py)

**Task:** Find all blog posts that have at least one comment.

### Exercise 2.2: Has Parent Query

See [`06_has_parent_query.py`](./06_has_parent_query.py)

**Task:** Find all comments on posts authored by a specific user.

### Exercise 2.3: Parent ID Query

See [`07_parent_id_query.py`](./07_parent_id_query.py)

**Task:** Retrieve all comments for a specific blog post.

### Exercise 2.4: Children Aggregation

See [`08_children_aggregation.py`](./08_children_aggregation.py)

**Task:** Calculate the average number of likes on comments per blog post.

## Part 3: Advanced Parent-Child Patterns

### Exercise 3.1: Inner Hits - Getting Related Documents

See [`09_inner_hits_comments.py`](./09_inner_hits_comments.py)

**Task:** Retrieve blog posts with their most recent 5 comments.

### Exercise 3.2: Scoring with Child Documents

See [`10_has_child_function_score.py`](./10_has_child_function_score.py)

**Task:** Score blog posts based on the number of comments they have.

### Exercise 3.3: Complex Multi-Level Queries

See [`11_multi_level_has_child.py`](./11_multi_level_has_child.py)

**Task:** Find comments that have replies from the original post author.

## Part 4: Performance Considerations

### Exercise 4.1: Compare Parent-Child vs Nested Performance

See [`12_query_performance_benchmark.py`](./12_query_performance_benchmark.py)

**Task:** Compare the performance of different parent-child query types.

### Exercise 4.2: Create Alternative Denormalized Structure

See [`13_denormalized_nested_structure.py`](./13_denormalized_nested_structure.py)

**Task:** Compare query complexity between parent-child and nested approaches.

## Part 5: Real-World Scenarios

### Exercise 5.1: E-commerce Product Reviews

See [`14_ecommerce_product_reviews.py`](./14_ecommerce_product_reviews.py)

**Task:** Create queries to find:

1. Products with more than 10 reviews
1. Products where all reviews are verified purchases
1. The top-rated products in each category

### Exercise 5.2: Company Organization Structure

See [`15_company_org_hierarchy.py`](./15_company_org_hierarchy.py)

**Task:** Implement a complete company hierarchy with:

1. Company -> Departments -> Employees
1. Queries to find departments over budget
1. Aggregations for salary statistics by department

## Best Practices and Considerations

### When to Use Parent-Child

1. **One-to-many relationships** where children are frequently updated
   independently
1. **Large child sets** that would make nested documents too large
1. **Need to query children independently** from parents
1. **Different update frequencies** between parent and child

### When NOT to Use Parent-Child

1. **Small datasets** - Overhead not worth it
1. **Rarely queried relationships** - Denormalization might be better
1. **Need high query performance** - Parent-child queries are slower
1. **Simple aggregations** - Nested might be sufficient

### Performance Tips

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

Write a script to migrate from a parent-child structure to a denormalized
structure and compare:

- Index size
- Query performance
- Update performance
- Memory usage

## Summary Questions

1. When should you use parent-child vs nested documents?
1. Why is routing required for child documents?
1. What are the performance implications of parent-child relationships?
1. How do inner_hits work and when should you use them?
1. What are the limitations of parent-child relationships in Elasticsearch?
