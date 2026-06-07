# Parent-Child Relationship Model for Hierarchical Data

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

See [`ex_1_1.py`](./ex_1_1.py)


**Task:** Create the index and understand the join field structure.

### Exercise 1.2: Index Parent Documents (Blog Posts)

See [`ex_1_2.py`](./ex_1_2.py)


**Task:** Index the parent documents and note how the `join_field` is set.

### Exercise 1.3: Index Child Documents (Comments)

See [`ex_1_3.py`](./ex_1_3.py)


**Task:** Index child documents and understand why routing is required.

### Exercise 1.4: Index Grandchild Documents (Replies to Comments)

See [`ex_1_4.py`](./ex_1_4.py)


**Task:** Understand the routing requirements for multi-level hierarchies.

## Part 2: Querying Parent-Child Relationships

### Exercise 2.1: Has Child Query

See [`ex_2_1.py`](./ex_2_1.py)


**Task:** Find all blog posts that have at least one comment.

### Exercise 2.2: Has Parent Query

See [`ex_2_2.py`](./ex_2_2.py)


**Task:** Find all comments on posts authored by a specific user.

### Exercise 2.3: Parent ID Query

See [`ex_2_3.py`](./ex_2_3.py)


**Task:** Retrieve all comments for a specific blog post.

### Exercise 2.4: Children Aggregation

See [`ex_2_4.py`](./ex_2_4.py)


**Task:** Calculate the average number of likes on comments per blog post.

## Part 3: Advanced Parent-Child Patterns

### Exercise 3.1: Inner Hits - Getting Related Documents

See [`ex_3_1.py`](./ex_3_1.py)


**Task:** Retrieve blog posts with their most recent 5 comments.

### Exercise 3.2: Scoring with Child Documents

See [`ex_3_2.py`](./ex_3_2.py)


**Task:** Score blog posts based on the number of comments they have.

### Exercise 3.3: Complex Multi-Level Queries

See [`ex_3_3.py`](./ex_3_3.py)


**Task:** Find comments that have replies from the original post author.

## Part 4: Performance Considerations

### Exercise 4.1: Compare Parent-Child vs Nested Performance

See [`ex_4_1.py`](./ex_4_1.py)


**Task:** Compare the performance of different parent-child query types.

### Exercise 4.2: Create Alternative Denormalized Structure

See [`ex_4_2.py`](./ex_4_2.py)


**Task:** Compare query complexity between parent-child and nested approaches.

## Part 5: Real-World Scenarios

### Exercise 5.1: E-commerce Product Reviews

See [`ex_5_1.py`](./ex_5_1.py)


**Task:** Create queries to find:
1. Products with more than 10 reviews
2. Products where all reviews are verified purchases
3. The top-rated products in each category

### Exercise 5.2: Company Organization Structure

See [`ex_5_2.py`](./ex_5_2.py)


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
